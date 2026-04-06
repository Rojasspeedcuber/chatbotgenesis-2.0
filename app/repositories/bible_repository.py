from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List, Dict


class BibleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_verse(
        self,
        book_name: str,
        chapter: int,
        verse: int,
        version_name: str
    ) -> Optional[Dict]:
        """
        Busca um versículo específico.
        Assume que a tabela tem colunas: book, chapter, verse, text, version
        """
        query = text("""
            SELECT v.text, b.name as book_name, v.chapter, v.verse, vr.abbrev as version
            FROM verses v
            JOIN books b ON v.book_id = b.id
            JOIN versions vr ON v.version_id = vr.id
            WHERE LOWER(b.name) LIKE LOWER(:book_name)
            AND v.chapter = :chapter
            AND v.verse = :verse
            AND LOWER(vr.abbrev) = LOWER(:version)
            LIMIT 1
        """)
        
        result = self.db.execute(query, {
            "book_name": f"%{book_name}%",
            "chapter": chapter,
            "verse": verse,
            "version": version_name
        }).fetchone()
        
        if result:
            return dict(result._mapping)
        return None

    def get_chapter(
        self,
        book_name: str,
        chapter: int,
        version_name: str
    ) -> List[Dict]:
        """Busca todos os versículos de um capítulo."""
        query = text("""
            SELECT v.text, v.verse, b.name as book_name, vr.abbrev as version
            FROM verses v
            JOIN books b ON v.book_id = b.id
            JOIN versions vr ON v.version_id = vr.id
            WHERE LOWER(b.name) LIKE LOWER(:book_name)
            AND v.chapter = :chapter
            AND LOWER(vr.abbrev) = LOWER(:version)
            ORDER BY v.verse
        """)
        
        results = self.db.execute(query, {
            "book_name": f"%{book_name}%",
            "chapter": chapter,
            "version": version_name
        }).fetchall()
        
        return [dict(row._mapping) for row in results]

    def compare_verse_versions(
        self,
        book_name: str,
        chapter: int,
        verse: int,
        version_names: List[str]
    ) -> List[Dict]:
        """Compara um versículo em várias versões."""
        placeholders = ", ".join([f":version_{i}" for i in range(len(version_names))])
        params = {
            "book_name": f"%{book_name}%",
            "chapter": chapter,
            "verse": verse
        }
        
        for i, version in enumerate(version_names):
            params[f"version_{i}"] = version.lower()
        
        query = text(f"""
            SELECT v.text, v.verse, b.name as book_name, vr.abbrev as version
            FROM verses v
            JOIN books b ON v.book_id = b.id
            JOIN versions vr ON v.version_id = vr.id
            WHERE LOWER(b.name) LIKE LOWER(:book_name)
            AND v.chapter = :chapter
            AND v.verse = :verse
            AND LOWER(vr.abbrev) IN ({placeholders})
            ORDER BY v.id
        """)
        
        results = self.db.execute(query, params).fetchall()
        return [dict(row._mapping) for row in results]

    def search_reference(
        self,
        reference: str,
        version_name: str
    ) -> Optional[Dict]:
        """
        Busca por referência textual tipo 'João 3:16' ou '1Cor 13:4'.
        Parse básico implementado aqui para facilitar.
        """
        import re
        
        # Regex para capturar: Livro Capítulo:Versículo
        # Suporta: João 3:16, 1 João 3:16, 1João 3:16, etc
        pattern = r'(\d?\s?[a-zA-ZçÇãÃõÕíÍúÚóÓáÁéÉ]+)\s+(\d+):(\d+)'
        match = re.search(pattern, reference, re.IGNORECASE)
        
        if match:
            book = match.group(1).strip()
            chapter = int(match.group(2))
            verse = int(match.group(3))
            return self.get_verse(book, chapter, verse, version_name)
        
        return None