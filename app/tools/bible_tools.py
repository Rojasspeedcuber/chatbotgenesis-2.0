from sqlalchemy.orm import Session
from typing import List, Dict, Optional

from app.repositories.bible_repository import BibleRepository


def get_verse_tool(
    db: Session,
    book_name: str,
    chapter: int,
    verse: int,
    version_name: str = "NVI"
) -> Optional[Dict]:
    """Tool: Busca um versículo específico."""
    repo = BibleRepository(db)
    return repo.get_verse(book_name, chapter, verse, version_name)


def get_chapter_tool(
    db: Session,
    book_name: str,
    chapter: int,
    version_name: str = "NVI"
) -> List[Dict]:
    """Tool: Busca capítulo completo."""
    repo = BibleRepository(db)
    return repo.get_chapter(book_name, chapter, version_name)


def compare_versions_tool(
    db: Session,
    book_name: str,
    chapter: int,
    verse: int,
    version_names: List[str]
) -> List[Dict]:
    """Tool: Compara versículo em múltiplas versões."""
    repo = BibleRepository(db)
    return repo.compare_verse_versions(book_name, chapter, verse, version_names)


def search_reference_tool(
    db: Session,
    reference: str,
    version_name: str = "NVI"
) -> Optional[Dict]:
    """Tool: Busca por referência textual livre."""
    repo = BibleRepository(db)
    return repo.search_reference(reference, version_name)
