from typing import List, Dict


def format_bible_response(data: Dict) -> str:
    """Formata um versículo para resposta."""
    if not data:
        return "Não encontrei essa referência na Bíblia. Verifique se o livro existe e se a referência está correta (ex: João 3:16)."
    
    book = data.get("book_name", "")
    chapter = data.get("chapter", "")
    verse = data.get("verse", "")
    text = data.get("text", "")
    version = data.get("version", "NVI")
    
    return f"*{book} {chapter}:{verse}* ({version})\n\n{text}"


def format_chapter_response(verses: List[Dict], book_name: str, chapter: int) -> str:
    """Formata capítulo completo."""
    if not verses:
        return f"Capítulo {chapter} de {book_name} não encontrado."
    
    version = verses[0].get("version", "NVI")
    header = f"*{book_name} {chapter}* ({version})\n\n"
    
    body = "\n".join([
        f"{v.get('verse', '')}. {v.get('text', '')}" 
        for v in verses
    ])
    
    return header + body


def format_comparison_response(results: List[Dict], reference: str) -> str:
    """Formata comparação de versões."""
    if not results:
        return "Não encontrei essa referência nas versões solicitadas."
    
    lines = [f"*Comparação: {reference}*\n"]
    
    for result in results:
        version = result.get("version", "")
        text = result.get("text", "")
        lines.append(f"*{version}:*\n{text}\n")
    
    return "\n".join(lines)


def split_long_message(text: str, max_length: int = 3500) -> List[str]:
    """
    Divide mensagens longas para WhatsApp.
    Limite conservador de 3500 caracteres.
    """
    if len(text) <= max_length:
        return [text]
    
    parts = []
    current = ""
    
    # Tenta dividir por versículos ou parágrafos
    lines = text.split("\n")
    
    for line in lines:
        if len(current) + len(line) + 1 > max_length:
            if current:
                parts.append(current.strip())
            current = line + "\n"
        else:
            current += line + "\n"
    
    if current.strip():
        parts.append(current.strip())
    
    return parts
