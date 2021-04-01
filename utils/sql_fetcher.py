import os


class SqlFetcher:
	def __init__(self, sql_folder: str = ".") -> None:
		self.sql = {}
		self.sql_folder = sql_folder
		for path in [
			os.path.join(directory, file_name)
			for directory, _, file_names in os.walk(sql_folder)
			for file_name in file_names
			if file_name[-4:] == ".sql"
		]:
			self.fetch(path)  # load all sql files on initialisation

	def fetch(self, *paths: str):
		"""
		Fetches the SQL code in the file `file_name` located in the given directory.

		:param *paths: Path components, as would be passed to os.path.join(). Relative to `sql_folder` passed to the constructor.
		"""
		path = os.path.join(self.sql_folder, *paths)
		if path in self.sql:
			return self.sql[path]
		self.sql[path] = open(path, "r").read()
		return self.sql[path]