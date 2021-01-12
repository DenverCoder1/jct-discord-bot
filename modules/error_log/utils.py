import discord
import discord.utils
import os
import csv
from datetime import datetime

def get_discord_obj(iterable, label: str):
	def get_id(label: str):
		"""gets the id of an object that has the given label in the CSV file"""
		with open(os.path.join("modules", "new_user", "../../ids.csv")) as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=",")
			for row in csv_reader:
				if row[0] == label:
					return int(row[1])
			return None
	return discord.utils.get(iterable, id=get_id(label))

def get_logs(filename: str):
    """return the contents of a file"""
    with open(filename, "r", encoding="utf-8") as f:
        # return the contents of the log file
        return f.read()

def log_to_file(filename: str, text: str):
    """appends the date and logs text to a file"""
    with open(filename, "a", encoding="utf-8") as f:
        # write the current time and log text at end of file
        f.write(f"{datetime.now()}\n{text}\n")