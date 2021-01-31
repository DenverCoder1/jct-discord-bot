import discord

class XKCDEmbedder:
	def gen_embed(self, json: dict) -> discord.Embed:
		embed = discord.Embed(
			title=f"{json['num']}: {json['safe_title']}", 
			url=f"https://xkcd.com/{json['num']}",
			colour=discord.Colour.green()
		)
		embed.set_image(url=json['img'])
		embed.set_footer(text=json['alt'])
		return embed