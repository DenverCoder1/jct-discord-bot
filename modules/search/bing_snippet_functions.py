from .formatting import get_list_string, format_message
from bs4 import BeautifulSoup
import requests
from typing import Union

def get_question_snippet(question: str) -> Union[str, None]:
	"""Searches question on bing and returns a formatted snippet"""

	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

	snippet_class = "rwrl rwrl_pri rwrl_padref"
	snippet_link_class = "rwrl_cred rwrl_f"

	page = requests.get(f"https://www.bing.com/search?q={question.replace(' ', '+')}" + "&lang=en", headers=headers)
	html = BeautifulSoup(page.content, 'html.parser')

	result = ""
	snippet_html = html.find(class_=snippet_class)
	link_html = html.find(class_=snippet_link_class)
	link = link_html.find("cite").get_text() if link_html != None else ""

	if (snippet_html != None):
		if (snippet_html.find("ul") != None):
			result = get_list_string(snippet_html.find("ul"))
		
		elif (snippet_html.find("ol") != None):
			result = get_list_string(snippet_html.find("ol"))
		
		else:
			result = snippet_html.get_text()
	
	return f"{format_message(question, link, result)}" if result else None