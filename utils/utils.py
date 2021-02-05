import csv
from itertools import product
import os
from typing import Iterable, List, Mapping, Optional, Tuple
import discord
import re


class IdNotFoundError(Exception):
	def __init__(self, *args: object) -> None:
		super().__init__(*args)


def get_discord_obj(iterable, label: str):
	return discord.utils.get(iterable, id=get_id(label))


def get_id(label: str) -> int:
	"""gets the id of an object that has the given label in the CSV file"""
	with open(os.path.join("utils", "ids.csv")) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=",")
		for row in csv_reader:
			if row[0] == label:
				return int(row[1])
		raise IdNotFoundError(f"There is not ID labeled {label} in ids.csv")


def remove_tabs(string: str) -> str:
	"""removed up to limit_per_line (default infinitely many) tabs from the beginning of each line of string"""
	return re.sub(r"\n\t*", "\n", string).strip()


def blockquote(string: str) -> str:
	"""Add blockquotes to a string"""
	return re.sub(r"(^|\n)", r"\1> ", string)


def ordinal(n: int):
	return "%d%s" % (n, "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10 :: 4])


def decode_mention(mention: str) -> Tuple[Optional[str], Optional[int]]:
	"""returns whether mention is a member mention or a channel mention (or neither) as well as the id of the mentioned object"""
	match = re.search(r"<(#|@)!?(\d+)>", mention)
	if match is None:
		return None, None
	else:
		groups = match.groups()
		return "channel" if groups[0] == "#" else "member", groups[1]


def is_email(email: str) -> bool:
	return bool(re.search(r"^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$", email))


def build_aliases(
	name: str,
	prefix: Iterable[str],
	suffix: Iterable[str],
	more_aliases: Iterable[str] = (),
	include_dots: bool = True,
) -> Mapping:
	dots = ("", ".") if include_dots else ("")
	return {
		"name": name,
		"aliases": list(more_aliases)
		+ [a + b + c for a, b, c in product(prefix, dots, suffix) if a + b + c != name],
	}
