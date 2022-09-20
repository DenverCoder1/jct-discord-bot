import nextcord

from utils.embedder import build_embed

from .comic import Comic


class XKCDEmbedder:
    def gen_embed(self, comic: Comic) -> nextcord.Embed:
        embed = build_embed(
            title=f"{comic.num}: {comic.title}",
            footer=comic.alt,
            url=f"https://xkcd.com/{comic.num}",
            image=comic.img,
        )
        return embed
