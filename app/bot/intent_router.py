from typing import Dict, Any
from app.utils.bible_parser import parse_bible_reference


def detect_compare_intent(message: str) -> bool:
    keywords = ["comparar", "compare", "versões", "versoes"]
    lower_msg = message.lower()
    return any(keyword in lower_msg for keyword in keywords)


def route_intent(message: str) -> Dict[str, Any]:
    parsed = parse_bible_reference(message)

    if detect_compare_intent(message):
        return {
            "intent": "version_compare",
            "raw_message": message
        }

    if parsed:
        if parsed["type"] == "verse":
            return {
                "intent": "reference_lookup",
                **parsed
            }

        if parsed["type"] == "chapter":
            return {
                "intent": "chapter_lookup",
                **parsed
            }

    return {
        "intent": "unknown",
        "raw_message": message
    }
