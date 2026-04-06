from sqlalchemy.orm import Session

from app.config import settings
from app.bot.intent_router import route_intent
from app.bot.response_formatter import (
    format_verse_response,
    format_chapter_response,
    format_compare_response,
)
from app.repositories.bible_repository import BibleRepository


class BibleAgent:
    def __init__(self, db: Session):
        self.repository = BibleRepository(db)

    def handle_message(self, message: str) -> str:
        route = route_intent(message)
        intent = route["intent"]

        if intent == "reference_lookup":
            version = route.get("version") or settings.DEFAULT_BIBLE_VERSION

            verse = self.repository.get_verse(
                book_name=route["book"],
                chapter=route["chapter"],
                verse=route["verse"],
                version_name=version
            )

            if not verse:
                return "Não encontrei esse versículo nessa versão. Confere o nome do livro, capítulo, versículo e versão."

            return format_verse_response(verse)

        if intent == "chapter_lookup":
            version = route.get("version") or settings.DEFAULT_BIBLE_VERSION

            chapter_rows = self.repository.get_chapter(
                book_name=route["book"],
                chapter=route["chapter"],
                version_name=version
            )

            if not chapter_rows:
                return "Não encontrei esse capítulo nessa versão."

            return format_chapter_response(chapter_rows)

        if intent == "version_compare":
            return (
                "A comparação entre versões será a próxima etapa. "
                "Primeiro vamos validar bem a consulta por referência exata."
            )

        return (
            "Não consegui identificar a referência bíblica. "
            "Tente algo como: João 3:16 ou Salmos 23 na NVI."
        )
