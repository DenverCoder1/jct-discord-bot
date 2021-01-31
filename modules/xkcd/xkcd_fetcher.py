import requests
import random

class XKCDFetcher:
	def get_comic_by_id(self, comic_id: int) -> dict:
		"""returns the json of an XKCD comic given its id"""
		response = requests.get(f"https://xkcd.com/{comic_id}/info.0.json")
		if response.status_code != 200:
			# XKCD API did not return a 200 response code
			raise ConnectionError("Could not find a comic with that id.")
		# load json from response
		return response.json()
	
	def get_latest(self) -> dict:
		"""returns the json of the latest XKCD comic"""
		response = requests.get(f"https://xkcd.com/info.0.json")
		if response.status_code != 200:
			# XKCD API did not return a 200 response code
			raise ConnectionError("Failed to fetch the latest comic.")
		# load json from response
		return response.json()

	def get_latest_num(self) -> int:
		"""returns the comic number of the latest XKCD comic"""
		json = self.get_latest()
		return json['num']

	def get_random(self) -> dict:
		"""returns the json for a random XKCD comic"""
		random.seed()
		latest_num = self.get_latest_num()
		random_id = random.randrange(1, latest_num + 1)
		return self.get_comic_by_id(random_id)