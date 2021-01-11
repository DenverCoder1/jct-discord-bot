import config
from typing import List
import re


class JoinParseError(Exception):
	pass


class JoinParser:
	"""
	Parses a join command to obtain a member's name, campus, and year
	"""

	def __init__(self, command: str):
		if not command.startswith(f"{config.prefix}join"):
			raise ValueError(f"command must start with {config.prefix}join")

		self.command = command[len(config.prefix) + 4 :].strip()  # remove {prefix}join
		self.decomp = self.decompose()
		self.name = self.extract_name()
		self.campus = self.extract_campus()
		self.year = self.extract_year()

	def decompose(self, enforce_well_formed=True) -> List[str]:
		decomp = [component.strip() for component in self.command.split(",")]
		return decomp if len(decomp) == 4 or not enforce_well_formed else None

	def extract_name(self) -> str:
		# if there are 4 components (or more) take the first 2 components as first and last names
		if self.decomp is not None:
			return " ".join(
				[name.capitalize() for name in " ".join(self.decomp[:2]).split()]
			)

		# if only three components were found by splitting on comma
		# then assume the comma between first and last name was missed
		decomposition = self.decompose(enforce_well_formed=False)
		if len(decomposition) == 3:
			names = decomposition[0].split()
			if len(names) >= 2:
				return " ".join([name.capitalize() for name in names])

		# switch to fallback mode: look for first two words which aren't special
		return self.extract_name_fallback()

	def extract_name_fallback(self):
		def is_special(word):
			return word.lower() in {"machon", "lev", "tal"} or any(
				char.isdigit() for char in word
			)

		words = self.command.replace(",", " ").split()
		if len(words) < 2 or any(is_special(word) for word in words[:2]):
			raise JoinParseError(
				"Could not detect your full name. Please include your first and"
				" last names, as shown in the command description above."
			)

		return words[0].capitalize() + " " + words[1].capitalize()

	def extract_campus(self) -> str:
		string = (self.decomp[2] if self.decomp is not None else self.command).lower()
		has_lev = bool(re.search(r"\blev\b", string))
		has_tal = bool(re.search(r"\btal\b", string))
		if has_lev and not has_tal:
			return "Lev"
		elif has_tal and not has_lev:
			return "Tal"
		else:
			raise JoinParseError(
				"Could not detect the campus you're in. Please include either *Lev* or"
				" *Tal* as shown in the command description above."
			)

	def extract_year(self) -> int:
		string = self.decomp[3] if self.decomp is not None else self.command
		string = string.replace("first", "1")
		string = string.replace("second", "2")
		string = string.replace("third", "3")
		string = string.replace("fourth", "4")
		numbers = re.findall(r"[1-4]", string)
		if len(numbers) == 1:
			return int(numbers[0])
		elif len(numbers) < 1:
			raise JoinParseError(
				"Could not detect the year you're in. Please include one of *1*, *2*,"
				" *3*, or *4* as shown in the command description above."
			)
		else:
			raise JoinParseError(
				f"Could not determine which of {numbers} is your year. Please include"
				" **one** of *1*, *2*, *3*, or *4* as shown in the command description"
				" above."
			)
