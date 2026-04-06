from typing import List, Dict


def format_verse_response(data: Dict) -> str:
    return (
        f"{data['livro']} {data['capitulo']}:{data['versiculo']} — {data['versao']}\n\n"
        f"{data['texto']}"
    )


def format_chapter_response(rows: List[Dict]) -> str:
    if not rows:
        return "Não encontrei esse capítulo."

    header = f"{rows[0]['livro']} {rows[0]['capitulo']} — {rows[0]['versao']}\n"
    verses = [f"{row['versiculo']}. {row['texto']}" for row in rows]

    return header + "\n" + "\n".join(verses)


def format_compare_response(rows: List[Dict]) -> str:
    if not rows:
        return "Não encontrei versões para essa referência."

    reference = f"{rows[0]['livro']} {rows[0]['capitulo']}:{rows[0]['versiculo']}\n"
    parts = [reference]

    for row in rows:
        parts.append(f"{row['versao']}:\n{row['texto']}\n")

    return "\n".join(parts)
