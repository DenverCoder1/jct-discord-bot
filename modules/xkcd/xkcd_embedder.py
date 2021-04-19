from utils.embedder import build_embed
import discord
from .comic import Comic


class XKCDEmbedder:
	def gen_embed(self, comic: Comic) -> discord.Embed:
		embed = build_embed(
			title=f"{comic.num}: {comic.title}",
			url=f"https://xkcd.com/{comic.num}"
		)
		embed.set_image(url=comic.img)
		embed.set_footer(text=comic.alt)
		return embed