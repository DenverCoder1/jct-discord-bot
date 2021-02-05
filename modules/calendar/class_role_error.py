class ClassRoleError(Exception):
	"""Exception raised when a class role is missing
	or there are more class roles than expected."""

	def __init__(self, *args):
		self.args = args
