import random
from typing import Callable
from utils import utils
from utils.sql_fetcher import SqlFetcher
import discord
from pyluach.dates import HebrewDate
import psycopg2.extensions as sql


class Assigner:
	"""
	Assigns users their roles and name, and welcomes them once done.
	"""

	def __init__(
		self,
		guild: Callable[[], discord.Guild],
		conn: sql.connection,
		sql_fetcher: SqlFetcher,
	):
		self.guild = guild
		self.unassigned_role = guild().get_role(utils.get_id("UNASSIGNED_ROLE"))
		self.student_role = guild().get_role(utils.get_id("STUDENT_ROLE"))
		self.welcome_channel = guild().get_channel(utils.get_id("OFF_TOPIC_CHANNEL"))
		self.conn = conn
		self.sql_fetcher = sql_fetcher

	async def assign(
		self, member: discord.Member, name: str, campus_id: int, year: int
	):
		if self.unassigned_role in member.roles:
			await member.edit(nick=name)
			await self.__add_role(member, campus_id, year)
			await member.add_roles(self.student_role)
			await member.remove_roles(self.unassigned_role)
			print(f"Removed Unassigned from {member} and added Student")
			await self.server_welcome(member)

	async def __add_role(self, member: discord.Member, campus_id: int, year: int):
		"""adds the right role to the user that used the command"""
		today = HebrewDate.today()
		last_elul_year = today.year if today.month == 6 else today.year - 1
		last_elul = HebrewDate(last_elul_year, 6, 1)
		base_year = last_elul.to_pydate().year
		grad_year = base_year + 4 - year

		query = self.sql_fetcher.fetch("modules", "join", "queries", "get_role.sql")
		with self.conn as conn:
			with conn.cursor() as cursor:
				cursor.execute(query, {"campus_id": campus_id, "grad_year": grad_year})
				role_id = cursor.fetchone()[0]

		class_role = self.guild().get_role(role_id)

		await member.add_roles(class_role)
		print(f"Gave {class_role.name} to {member.display_name}")

	async def server_welcome(self, member: discord.Member):
		# Sets the channel to the welcome channel and sends a message to it
		welcome_emojis = ["🎉", "👋", "🌊", "🔥", "😎", "👏", "🎊", "🥳", "🙌", "✨", "⚡"]
		random_emoji = random.choice(welcome_emojis)
		nth = utils.ordinal(len(self.student_role.members))
		await self.welcome_channel.send(
			f"Everyone welcome our {nth} student {member.mention} to the"
			f" server! Welcome! {random_emoji}"
		)
