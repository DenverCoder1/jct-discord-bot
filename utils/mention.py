import re
from typing import Iterable, Optional, Tuple


def decode_mention(mention: str) -> Tuple[Optional[str], Optional[int]]:
    """returns whether mention is a member mention or a channel mention (or neither) as well as the id of the mentioned object"""
    match = re.search(r"<(#|@)!?(\d+)>", mention)
    if match is None:
        return None, None
    else:
        groups = match.groups()
        return "channel" if groups[0] == "#" else "member", int(groups[1])


def decode_channel_mention(mention: str) -> Optional[int]:
    """returns the id of a mentioned channel or none if it isn't a channel mention."""
    mention_type, mention_id = decode_mention(mention)
    return mention_id if mention_type == "channel" else None


def decode_member_mention(mention: str) -> Optional[int]:
    """returns the id of a mentioned channel or none if it isn't a channel mention."""
    mention_type, mention_id = decode_mention(mention)
    return mention_id if mention_type == "member" else None


def extract_mentions(string: str, filter_function=None) -> Iterable[str]:
    filter_function = filter_function or (lambda x: x)
    return [match for match in re.findall(r"<[^>]+>", string) if filter_function(match)]


def extract_channel_mentions(string: str) -> Iterable[str]:
    return extract_mentions(string, decode_channel_mention)


def extract_member_mentions(string: str) -> Iterable[str]:
    return extract_mentions(string, decode_member_mention)
