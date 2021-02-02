from discord.ext import commands
import discord


class NewHelpCommand(commands.MinimalHelpCommand):
	"""Custom help command override using embeds"""

	# embed colour
	COLOUR = discord.Colour.blurple()

	def get_command_signature(self, command: commands.core.Command):
		"""Retrieves the signature portion of the help page."""
		prefix = self.clean_prefix
		return f"{prefix}{command.qualified_name} {command.signature}"

	async def send_bot_help(self, mapping: dict):
		"""implements bot command help page"""
		prefix = self.clean_prefix
		invoked_with = self.invoked_with
		embed = discord.Embed(title="Bot Commands", colour=self.COLOUR)
		embed.description = (
			f'Use "{prefix}{invoked_with} command" for more info on a command.\n' 
			f'Use "{prefix}{invoked_with} category" for more info on a category.'
		)

		for cog, commands in mapping.items():
			name = "No Category" if cog is None else cog.qualified_name
			filtered = await self.filter_commands(commands, sort=True)
			if filtered:
				# \u2002 = middle dot
				value = "\u2002".join(f"`{prefix}{c.name}`" for c in commands)
				if cog and cog.description:
					value = f"{cog.description}\n{value}"
				embed.add_field(name=name, value=value, inline=True)

		await self.get_destination().send(embed=embed)

	async def send_cog_help(self, cog: commands.Cog):
		"""implements cog help page"""
		embed = discord.Embed(
			title=f"{cog.qualified_name} Commands", colour=self.COLOUR
		)
		if cog.description:
			embed.description = cog.description

		filtered = await self.filter_commands(cog.get_commands(), sort=True)
		for command in filtered:
			embed.add_field(
				name=self.get_command_signature(command),
				value=command.short_doc or "...",
				inline=False
			)

		await self.get_destination().send(embed=embed)

	async def send_group_help(self, group: commands.Group):
		"""implements group help page and command help page"""
		embed = discord.Embed(title=group.qualified_name, colour=self.COLOUR)
		if group.help:
			embed.description = group.help

		if isinstance(group, commands.Group):
			filtered = await self.filter_commands(group.commands, sort=True)
			for command in filtered:
				embed.add_field(
					name=self.get_command_signature(command),
					value=command.short_doc or "...",
					inline=False
				)

		await self.get_destination().send(embed=embed)

	# Use the same function as group help for command help
	send_command_help = send_group_help