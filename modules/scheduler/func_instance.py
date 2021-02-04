from typing import Tuple


class FuncInstance:
	"""
	Represents an instance of a function call. I.e. a function with its arguments
	"""

	def __init__(self, func, args: Tuple = (), kwargs: Tuple = ()) -> None:
		self.func = func
		self.args = args
		self.kwargs = kwargs

	def call(self):
		self.func(*self.args, **self.kwargs)