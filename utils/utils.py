import csv
import os
import discord
import re


def get_discord_obj(iterable, label: str):
	return discord.utils.get(iterable, id=get_id(label))


def get_id(label: str):
	"""gets the id of an object that has the given label in the CSV file"""
	with open(os.path.join("utils", "ids.csv")) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=",")
		for row in csv_reader:
			if row[0] == label:
				return int(row[1])
		return None


def remove_tabs(string: str) -> str:
	"""removed up to limit_per_line (default infinitely many) tabs from the beginning of each line of string"""
	return re.sub(r"\n\t*", "\n", string).strip()