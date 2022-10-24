from typing import Iterable

import nextcord

from database.person import Person
from utils.embedder import build_embed


def gen_embed(person: Person):
    return build_embed(
        title=person.name,
        description=f"{person.linked_emails}\n{person.categories}".strip() or "No info found.",
        colour=nextcord.Colour.teal(),
    )


def gen_embeds(people: Iterable[Person]):
    return [gen_embed(person) for person in people]
