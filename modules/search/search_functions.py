import requests
from bs4 import BeautifulSoup
from googlesearch import search
import discord

def remove_citations(wiki_paragraph):
		"""removes citations from a string from a wiki"""
		while True:
			start_of_brackets = wiki_paragraph.find('[')
			end_of_brackets = wiki_paragraph.find(']')
	
			if start_of_brackets != -1 and end_of_brackets != -1:
				wiki_paragraph = wiki_paragraph[:start_of_brackets] + wiki_paragraph[end_of_brackets+1:]
			else:
				break
		return wiki_paragraph


def get_wiki(searched_string):
	"""Does basic setup and formatting of a given wiki page. Returns the plain text of the article."""
	url = search(searched_string + " wikipedia", num_results=1) # try to get a wiki link from google

	exception_caught = False
	while True:
		try:
			wiki_info = requests.get(url if exception_caught else url[0]) #If the googled link doesn't work or doesn't exist the URL should not be treated as a list
			page = BeautifulSoup(wiki_info.content, "html.parser")
			wiki_html = page.find(id="bodyContent").find_all("p")
			break

		except (IndexError, AttributeError): # if there is no link recieved the first time or the link isn't from wikipedia
			url = "https://en.wikipedia.org/wiki/" + searched_string
			exception_caught = True
	return wiki_html


def get_wiki_intro(wiki, last_paragraph):
	"""finds the into to the wiki from the text of the wiki"""
	
	# iterate through the paragraphs of the wiki
	for i in wiki:
		viable_wiki = True
	
		current_paragraph = i.get_text()

		# can remove bad articles by checking the length of the current paragraph
		if (len(current_paragraph) < 150):
			viable_wiki = False

		# " is " and " was " will be one of the first words in 99.99% of wiki intros
		if (" is " in current_paragraph) or (" was " in current_paragraph):
			if viable_wiki == True:
				last_paragraph[0] = i
			break

	if viable_wiki:
		return f"\n{remove_citations(current_paragraph)}-From Wikipedia.\n"
	else:
		return ""


async def next_paragraph(ctx, last_paragraph):
	"""finds the next paragraph in the last searched wiki"""
	if last_paragraph[0] != None:
		try: # attempt to get the next paragraph in the wiki
			next_paragraph = last_paragraph[0].find_next("p")
			await ctx.send(remove_citations(next_paragraph.get_text()))
			last_paragraph[0] = next_paragraph
	
		except discord.HTTPException: # raised when trying to get a non existent piece of html
			await ctx.send("The end of the search has been reached.")
			last_paragraph[0] = None
	else:
		await ctx.send("There is no search to continue.")


async def send_message(ctx, searched_string, wiki_string, link):
	"""formats and sends the message"""
	try:
		await ctx.send(
			f"""Search results for: {searched_string}
			{wiki_string}
{link[0]}""")
	except IndexError:
		await ctx.send("No search results found.")