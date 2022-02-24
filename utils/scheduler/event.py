from collections import defaultdict
from typing import DefaultDict, List
from .func_instance import FuncInstance
from nextcord.ext import commands


class Event:
	def __init__(self) -> None:
		self.func_instances: DefaultDict[int, List[FuncInstance]] = defaultdict(list)

	def add_function(self, func_instance: FuncInstance, dependency_index: int = 0):
		self.func_instances[dependency_index].append(func_instance)

	async def fire(self, bot: commands.Bot):
		for dependency_index in sorted(self.func_instances):
			for instance in self.func_instances[dependency_index]:
				await instance.call(bot.cogs)