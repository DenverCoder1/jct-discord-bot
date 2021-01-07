def translate(message : str):
	def first_two(str):
		return str[0]+str[1]
	lst = ['sh', 'gl', 'ch', 'ph', 'tr', 'br', 'fr', 'bl', 'gr', 'st', 'sl', 'cl', 'pl', 'fl']
	sentence = message.split(' ')
	for k in range(len(sentence)):
		i = sentence[k]
		if i[0] in ['a', 'e', 'i', 'o', 'u']:
			sentence[k] = i+'ay'
		elif first_two(i) in lst:
			sentence[k] = i[2:]+i[:2]+'ay'
		elif i.isalpha() == False:
			sentence[k] = i
		else:
			sentence[k] = i[1:]+i[0]+'ay'
	return ' '.join(sentence)