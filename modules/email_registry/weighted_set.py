from collections import defaultdict
from typing import Any, Set


class WeightedSet:
	def __init__(self) -> None:
		self.weights = defaultdict(int)

	def __getitem__(self, item: Any) -> int:
		return self.weights[item]

	def __setitem__(self, item: Any, weight: int) -> None:
		self.weights[item] = weight

	def heaviest_items(self) -> Set[Any]:
		"""Finds all the items with maximal weight"""
		items = {}
		max_weight = 0
		for item, weight in self.weights.items():
			if weight > max_weight:
				items = {item}
				max_weight = weight
			elif weight == max_weight:
				items.add(item)
		return items