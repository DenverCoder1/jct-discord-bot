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
		mentioned_channels: List[discord.TextChannel] = None,
		curr_channel: discord.TextChannel = None,
		mentioned_members: List[discord.Member] = None,
	) -> Set[Professor]:
		"""returns a list of professors who best match the query"""
		teachers = TeacherWeights()

		cursor = self.conn.cursor()

		# add all teachers found by mention of the channel of a course they teach
		for channel in mentioned_channels:
			for t_id in self.__search_channel(channel.id, cursor):
				teachers[t_id] += self.search_weights["mentioned_channel"]

		# add the teachers of the current channel
		for t_id in self.__search_channel(curr_channel.id, cursor) or []:
			teachers[t_id] += self.search_weights["curr_channel"]

		# add the teacher found (if any) by mention of their discord accont
		for member in mentioned_members:
			t_id = self.__search_member(member.id, cursor)
			if t_id is not None:
				teachers[t_id] += self.search_weights["mentioned_teacher"]

		# add all teachers whose name/course match the search query
		for keyword in query:
			for t_id in self.__search_kw(keyword, cursor):
				teachers[t_id] += self.search_weights["keyword"]

		professors = self.__get_professors(teachers.best_matches(), cursor)
		cursor.close()
		return professors

	def __search_channel(self, id: int, cursor: sql.cursor) -> Set[int]:
		"""searches the database for a channel id and returns the IDs of the teachers who teach that course"""
		query = open(os.path.join("queries", "search_channel.sql"), "r").read()
		return {row[0] for row in cursor.execute(query, {"channel_id": id}).fetchall()}

	def __search_member(self, id: int, cursor: sql.cursor) -> Optional[int]:
		"""searches the database for a teacher's id and returns the IDs of the teachers who match it"""
		query = open(os.path.join("queries", "search_member.sql"), "r").read()
		row = cursor.execute(query, {"member_id": id}).fetchone()
		return row[0] if row is not None else None

	def __search_kw(self, keyword: str, cursor: sql.cursor) -> Set[int]:
		"""searches the database for a single keyword and returns the IDs of the teachers who match it"""
		query = open(os.path.join("queries", "search_kw.sql"), "r").read()
		return {row[0] for row in cursor.execute(query, {"kw": keyword}).fetchall()}

	def __get_professors(
		self, ids: Iterable[int], cursor: sql.cursor
	) -> Set[Professor]:
		"""searches the database for a teacher with a given id and returns a Professor object"""
		query = open(os.path.join("queries", "get_professors.sql"), "r").read()
		data = cursor.execute(query, {"ids", ids}).fetchall()
		return {Professor(row[0], row[1], row[2]) for row in data}
