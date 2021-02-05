from typing import Mapping, Tuple
from discord.ext import commands


class FuncInstance:
	"""
	Represents an instance of a function call. I.e. a function with its arguments
	"""

	def __init__(self, func, args: Tuple = (), kwargs: Mapping = None) -> None:
		self.func = func
		self.args = args
		self.kwargs = kwargs or {}

	async def call(self, cogs: Mapping[str, commands.Cog]):
		for cog_name in cogs:
			try:
				if getattr(cogs[cog_name], self.func.__name__).__func__ == self.func:
					await self.func(cogs[cog_name], *self.args, **self.kwargs)
			except AttributeError:
				pass