import re
from typing import Optional, Dict


def parse_bible_reference(message: str) -> Optional[Dict]:
    """
    Exemplos aceitos:
    - João 3:16
    - joão 3:16 na NVI
    - Salmos 23
    - Romanos 8:28
    """
    text = message.strip()

    verse_pattern = re.compile(
        r"^(?P<book>[1-3]?\s?[A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+)*)\s+"
        r"(?P<chapter>\d+):(?P<verse>\d+)"
        r"(?:\s+na\s+(?P<version>.+))?$",
        re.IGNORECASE
    )

    chapter_pattern = re.compile(
        r"^(?P<book>[1-3]?\s?[A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+)*)\s+"
        r"(?P<chapter>\d+)"
        r"(?:\s+na\s+(?P<version>.+))?$",
        re.IGNORECASE
    )

    verse_match = verse_pattern.match(text)
    if verse_match:
        return {
            "type": "verse",
            "book": verse_match.group("book").strip(),
            "chapter": int(verse_match.group("chapter")),
            "verse": int(verse_match.group("verse")),
            "version": verse_match.group("version").strip() if verse_match.group("version") else None
        }

    chapter_match = chapter_pattern.match(text)
    if chapter_match:
        return {
            "type": "chapter",
            "book": chapter_match.group("book").strip(),
            "chapter": int(chapter_match.group("chapter")),
            "version": chapter_match.group("version").strip() if chapter_match.group("version") else None
        }

    return None