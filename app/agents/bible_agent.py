import re
from typing import Optional, List
from sqlalchemy.orm import Session

from app.tools.bible_tools import (
    get_verse_tool,
    get_chapter_tool,
    compare_versions_tool,
    search_reference_tool,
)
from app.tools.formatting_tools import (
    format_bible_response,
    format_chapter_response,
    format_comparison_response,
    split_long_message,
)


class BibleAgent:
    def __init__(self, db: Session, default_version: str = "NVI"):
        self.db = db
        self.default_version = default_version

    def handle_message(self, message: str) -> str:
        """
        Processa mensagem do usuário e retorna resposta.
        """
        message = message.strip()
        
        # Verifica se é comparação de versões
        if "comparar" in message.lower() or "versões" in message.lower():
            return self._handle_comparison(message)
        
        # Verifica se é capítulo completo
        if "capítulo" in message.lower() and ":" not in message:
            return self._handle_chapter_request(message)
        
        # Tenta extrair referência bíblica (João 3:16, 1Cor 13:4, etc)
        reference = self._extract_reference(message)
        if reference:
            return self._handle_verse(reference)
        
        # Busca livre
        if len(message) > 3:
            result = search_reference_tool(self.db, message, self.default_version)
            if result:
                return format_bible_response(result)
        
        return (
            "Olá! Sou o assistente bíblico. 📖\n\n"
            "Envie uma referência como:\n"
            "• João 3:16\n"
            "• Salmos 23\n"
            "• 1 Coríntios 13:4-7\n\n"
            "Ou peça para comparar versões: 'Comparar João 3:16 em NVI e ARC'"
        )

    def _extract_reference(self, text: str) -> Optional[dict]:
        """
        Extrai referência bíblica do texto.
        Retorna dict com book, chapter, verse_start, verse_end (opcional)
        """
        # Regex para capturar: Livro Cap:Vers ou Livro Cap:Vers-Vers
        # Ex: João 3:16, 1 João 3:16, 1João 3:16-18
        pattern = r'(\d?\s?[a-zA-ZçÇãÃõÕíÍúÚóÓáÁéÉêÊôÔ]+)\s+(\d+):(\d+)(?:-(\d+))?'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            return {
                "book": match.group(1).strip(),
                "chapter": int(match.group(2)),
                "verse": int(match.group(3)),
                "verse_end": int(match.group(4)) if match.group(4) else None
            }
        return None

    def _handle_verse(self, ref: dict) -> str:
        """Processa pedido de versículo."""
        if ref.get("verse_end"):
            # Se tem intervalo, pega o primeiro e indica que tem mais
            result = get_verse_tool(
                self.db,
                ref["book"],
                ref["chapter"],
                ref["verse"],
                self.default_version
            )
            if result:
                response = format_bible_response(result)
                response += f"\n\n_(Mostrando {ref['book']} {ref['chapter']}:{ref['verse']}. Para ver até o versículo {ref['verse_end']}, peça o capítulo completo)_"
                return response
        else:
            result = get_verse_tool(
                self.db,
                ref["book"],
                ref["chapter"],
                ref["verse"],
                self.default_version
            )
            if result:
                return format_bible_response(result)
        
        return f"Não encontrei {ref['book']} {ref['chapter']}:{ref['verse']}. Verifique a referência."

    def _handle_chapter_request(self, message: str) -> str:
        """Processa pedido de capítulo completo."""
        # Extrai livro e capítulo
        pattern = r'([a-zA-ZçÇãÃõÕíÍúÚóÓáÁéÉêÊôÔ]+)\s+(\d+)'
        match = re.search(pattern, message, re.IGNORECASE)
        
        if match:
            book = match.group(1)
            chapter = int(match.group(2))
            
            verses = get_chapter_tool(self.db, book, chapter, self.default_version)
            if verses:
                response = format_chapter_response(verses, book, chapter)
                # Divide se for muito longo
                parts = split_long_message(response)
                return parts[0] if parts else "Erro ao formatar capítulo."
        
        return "Não consegui entender qual capítulo você quer. Tente: 'Salmos 23' ou 'Gênesis 1'"

    def _handle_comparison(self, message: str) -> str:
        """Processa comparação de versões."""
        # Extrai referência
        ref = self._extract_reference(message)
        if not ref:
            return "Para comparar, envie: 'Comparar João 3:16 em NVI e ARC'"
        
        # Detecta versões mencionadas
        versions = self._extract_versions(message)
        if len(versions) < 2:
            versions = ["NVI", "ARC"]  # Padrão se não especificar
        
        results = compare_versions_tool(
            self.db,
            ref["book"],
            ref["chapter"],
            ref["verse"],
            versions
        )
        
        reference_str = f"{ref['book']} {ref['chapter']}:{ref['verse']}"
        return format_comparison_response(results, reference_str)

    def _extract_versions(self, text: str) -> List[str]:
        """Extrai siglas de versões do texto (NVI, ARC, KJV, etc)."""
        common_versions = ["NVI", "ARC", "KJV", "NAA", "NTLH", "JFA", "ARA"]
        found = []
        
        for version in common_versions:
            if version.lower() in text.lower():
                found.append(version)
        
        return found if found else ["NVI"]
