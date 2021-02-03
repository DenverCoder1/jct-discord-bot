class FuncInstance:
	"""
	Represents an instance of a function call. I.e. a function with its arguments
	"""

	def __init__(self, func, args, kwargs) -> None:
		self.func = func
		self.args = args
		self.kwargs = kwargs