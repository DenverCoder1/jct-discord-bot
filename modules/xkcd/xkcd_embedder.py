import discord

class XKCDEmbedder:
	def gen_embed(self, id: int, json: dict) -> discord.Embed:
		embed = discord.Embed(
			title=f"{id}: {json['safe_title']}", 
			url=f"https://xkcd.com/{id}", 
			colour=discord.Colour.green()
		)
		embed.set_image(url=json['img'])
		embed.set_footer(text=json['alt'])
		return embed