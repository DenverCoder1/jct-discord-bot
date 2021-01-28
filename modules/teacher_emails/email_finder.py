import os
from modules.teacher_emails.teacher_weights import TeacherWeights
from typing import Iterable, Set, List, Optional
from modules.teacher_emails.professor import Professor
import discord
import psycopg2.extensions as sql


class EmailFinder:
	def __init__(self, conn: sql.connection) -> None:
		self.conn = conn
		self.search_weights = {
			"keyword": 1,
			"curr_channel": 2,
			"mentioned_channel": 10,
			"mentioned_teacher": 20,
		}

	def search(
		self,
		query: List[str],
		mentioned_channels: List[discord.TextChannel],
		curr_channel: discord.TextChannel,
		mentioned_members: List[discord.Member],
	) -> Set[Professor]:
		"""returns a list of professors who best match the query"""
		teachers = TeacherWeights()

		# add all teachers found by mention of the channel of a course they teach
		for channel in mentioned_channels:
			for t_id in self.__search_channel(channel.id):
				teachers[t_id] += self.search_weights["mentioned_channel"]

		# add the teachers of the current channel
		for t_id in self.__search_channel(curr_channel.id) or []:
			teachers[t_id] += self.search_weights["curr_channel"]

		# add the teacher found (if any) by mention of their discord accont
		for member in mentioned_members:
			t_id = self.__search_member(member.id)
			if t_id is not None:
				teachers[t_id] += self.search_weights["mentioned_teacher"]

		# add all teachers whose name/course match the search query
		for keyword in query:
			for t_id in self.__search_kw(keyword):
				teachers[t_id] += self.search_weights["keyword"]

		professors = self.__get_professors(teachers.best_matches())
		return professors

	def __search_channel(self, id: int) -> Set[int]:
		"""searches the database for a channel id and returns the IDs of the teachers who teach that course"""
		query = open(self.__sql_path("search_channel.sql"), "r").read()
		cursor = self.conn.cursor()
		cursor.execute(query, {"channel_id": id})
		ids = {row[0] for row in cursor.fetchall()}
		cursor.close()
		return ids

	def __search_member(self, id: int) -> Optional[int]:
		"""searches the database for a teacher's id and returns the IDs of the teachers who match it"""
		query = open(self.__sql_path("search_member.sql"), "r").read()
		cursor = self.conn.cursor()
		row = cursor.execute(query, {"member_id": id}).fetchone()
		cursor.close()
		return row[0] if row is not None else None

	def __search_kw(self, keyword: str) -> Set[int]:
		"""searches the database for a single keyword and returns the IDs of the teachers who match it"""
		query = open(self.__sql_path("search_kw.sql"), "r").read()
		cursor = self.conn.cursor()
		cursor.execute(query, {"kw": keyword})
		ids = {row[0] for row in cursor.fetchall()}
		cursor.close()
		return ids

	def __get_professors(self, ids: Iterable[int]) -> Set[Professor]:
		"""searches the database for a teacher with a given id and returns a Professor object"""
		if not ids:
			return set()
		query = open(self.__sql_path("get_professors.sql"), "r").read()
		cursor = self.conn.cursor()
		cursor.execute(query, {"ids": tuple(ids)})
		profs = {Professor(row[0], row[1], row[2]) for row in cursor.fetchall()}
		cursor.close()
		return profs

	def __sql_path(self, file):
		return os.path.join("modules", "teacher_emails", "queries", file)