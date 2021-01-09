
import os
from discord import utils
from discord.ext import commands
from modules.new_user.new_user import *

class NewUser(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot


    @commands.command(name='join')
    async def join(self, ctx, first_name : str, last_name : str, machon : str, year : str):
        '''Join command to get new users information and place them in the right roles'''        
        
        #user who wrote the command
        member = ctx.author
        
        if not is_new(member):
            return
    
        await add_role(ctx, machon, year)
        await remove_unassigned(member)
        await change_nick(member, first_name, last_name)
            
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        '''catch missing required argument error'''
        
        if isinstance(error, commands.MissingRequiredArgument):
            if not is_new(ctx.message.author):
                return
            
            await ctx.send("The format is: ~join <first name> <last name> <Lev or Tal> <year in college (1, 2, or 3)>\n For example: ~join Moshe Rabbeinu lev 1")
    
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        '''Welcome members who join.'''
        print(f"{member.name} joined the guild.")
        
        #Sets the channel to the welcome channel and sends a message to it
        channel = utils.get(member.guild.channels, id = int(os.getenv("WELCOME_CHANNEL_ID")))#I'm not positive this is what the channel is called
        await channel.send(f"Welcome, {member.name}, please use the join command to continue. ~join <firstname> <lastname> <Lev or Tal> <year in college (1, 2, or 3)>")



#setup functions for bot
def setup(bot):
    bot.add_cog(NewUser(bot))