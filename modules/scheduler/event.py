from collections import defaultdict
from typing import DefaultDict, Dict, List
from .func_instance import FuncInstance


class Event:
	def __init__(self) -> None:
		self.func_instances: DefaultDict[int, List[FuncInstance]] = defaultdict(list)

	def add_function(self, func_instance, dependency_index: int = 0):
		self.func_instances[dependency_index].append(func_instance)

	def fire(self):
		for dependency_index in sorted(self.func_instances):
			for instance in self.func_instances[dependency_index]:
				instance.call()