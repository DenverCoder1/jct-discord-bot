import requests
import random
from .comic import Comic


class XKCDFetcher:
	def get_comic_by_id(self, comic_id: int) -> Comic:
		"""returns a Comic object of an xkcd comic given its id"""
		response = requests.get(f"https://xkcd.com/{comic_id}/info.0.json")
		if response.status_code != 200:
			# xkcd API did not return a 200 response code
			if response.status_code == 404:
				raise ConnectionError("That comic does not exist... yet.")
			raise ConnectionError(
				f"An unknown error occurred: HTTP {response.status_code}"
			)
		# load json from response
		comic = response.json()
		return Comic(comic["num"], comic["safe_title"], comic["alt"], comic["img"])

	def get_latest(self) -> Comic:
		"""returns a Comic object of the latest xkcd comic"""
		response = requests.get("https://xkcd.com/info.0.json")
		if response.status_code != 200:
			# xkcd API did not return a 200 response code
			raise ConnectionError(
				f"Failed to fetch the latest comic: HTTP {response.status_code}"
			)
		# load json from response
		comic = response.json()
		return Comic(comic["num"], comic["safe_title"], comic["alt"], comic["img"])

	def get_latest_num(self) -> int:
		"""returns the comic number of the latest xkcd comic"""
		comic = self.get_latest()
		return comic.num

	def get_random(self) -> Comic:
		"""returns a Comic object for a random xkcd comic"""
		random.seed()
		latest_num = self.get_latest_num()
		random_id = random.randrange(1, latest_num + 1)
		return self.get_comic_by_id(random_id)

	def search_relevant(self, search: str) -> Comic:
		relevant_xkcd_url = "https://relevant-xkcd-backend.herokuapp.com/search"
		body = {"search": search}
		response = requests.post(relevant_xkcd_url, data=body)
		data = response.json()
		if response.status_code != 200 and data["message"]:
			# Relevant xkcd did not return a 200 response code
			raise ConnectionError("Failed to fetch search results.")
		elif len(data["results"]) == 0:
			# Relevant xkcd did not return any results
			raise ConnectionError("No results found.")
		comic = data["results"][0]
		return Comic(
			comic["number"], comic["title"], comic["titletext"], comic["image"]
		)
