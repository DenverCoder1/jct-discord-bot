class ClassParseError(Exception):
	"""Exception raised when trying to parse a
	graduation year and campus for a class"""

	def __init__(self, *args):
		self.args = args
