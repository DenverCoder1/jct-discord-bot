from collections import defaultdict
from typing import Set
from modules.teacher_emails.professor import Professor


class TeacherWeights:
	def __init__(self) -> None:
		self.weights = defaultdict(int)

	def __getitem__(self, key):
		return self.weights[key]

	def __setitem__(self, key, value):
		self.weights[key] = value

	def best_matches(self) -> Set[int]:
		teachers = {}
		max_weight = 0
		for t_id, weight in self.weights.items():
			if weight > max_weight:
				teachers = {t_id}
				max_weight = weight
			elif weight == max_weight:
				teachers.add(t_id)
		return teachers