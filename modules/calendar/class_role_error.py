class ClassRoleError(Exception):
	def __init__(self, *args):
		self.args = args