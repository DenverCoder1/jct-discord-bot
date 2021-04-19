from utils.embedder import embed_success
import discord
from .comic import Comic


class XKCDEmbedder:
	def gen_embed(self, comic: Comic) -> discord.Embed:
		embed = embed_success(
			title=f"{comic.num}: {comic.title}",
			url=f"https://xkcd.com/{comic.num}",
			colour=discord.Colour.blurple(),
		)
		embed.set_image(url=comic.img)
		embed.set_footer(text=comic.alt)
		return embed