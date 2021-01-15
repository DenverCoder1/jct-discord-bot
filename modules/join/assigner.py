import discord
import utils.utils as utils


class Assigner:
	"""
	Assigns users their roles and name
	"""

	def __init__(self, guild: discord.Guild):
		self.unassigned_role = guild.get_role(utils.get_id("UNASSIGNED_ROLE_ID"))
		self.assigned_role = guild.get_role(utils.get_id("ASSIGNED_ROLE_ID"))

	async def assign(self, member: discord.Member, name: str, campus: str, year: int):
		if self.unassigned_role in member.roles:
			await member.edit(nick=name)
			await self.__add_role(member, campus, year)
			await member.add_roles(self.assigned_role)
			await member.remove_roles(self.unassigned_role)
			print(f"Removed Unassigned from {member} and added Assigned")

	async def __add_role(self, member: discord.Member, campus: str, year: int):
		"""adds the right role to the user that used the command"""
		# formatting role for csv file, eg LEV_YEAR_1_ROLE_ID
		role_label = f"{campus.upper()}_YEAR_{year}_ROLE_ID"
		class_role = utils.get_discord_obj(member.guild.roles, role_label)

		# check if the role was found
		if class_role == None:
			raise ValueError(f"Could not find the role for {role_label}.")

		await member.add_roles(class_role)
		print(f"Gave {class_role.name} to {member.display_name}")
