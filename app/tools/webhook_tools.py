from typing import Dict, Optional


def extract_incoming_message(payload: Dict) -> str:
    """
    Extrai mensagem do payload da EvolutionAPI.
    Adaptado para o formato padrão da EvolutionAPI v2.
    """
    if not isinstance(payload, dict):
        return ""
    
    # Tenta extrair de vários formatos possíveis
    # Formato 1: { "data": { "message": { "conversation": "texto" } } }
    data = payload.get("data", {})
    if isinstance(data, dict):
        message = data.get("message", {})
        if isinstance(message, dict):
            text = message.get("conversation", "")
            if text:
                return str(text)
        
        # Formato 2: { "data": { "text": "texto" } }
        text = data.get("text", "")
        if text:
            return str(text)
    
    # Formato 3: { "message": "texto" }
    msg = payload.get("message", "")
    if msg:
        return str(msg)
    
    # Formato 4: { "body": "texto" }
    body = payload.get("body", "")
    if body:
        return str(body)
    
    return ""


def extract_sender_info(payload: Dict) -> Dict:
    """Extrai informações do remetente."""
    data = payload.get("data", {}) if isinstance(payload, dict) else {}
    
    return {
        "remote_jid": data.get("key", {}).get("remoteJid", "unknown"),
        "push_name": data.get("pushName", "Usuário"),
        "instance": payload.get("instance", "default")
    }


def build_whatsapp_response(text: str) -> Dict:
    """
    Constrói resposta no formato esperado pela EvolutionAPI.
    """
    return {
        "message": text
    }


def validate_evolution_payload(payload: Dict) -> bool:
    """Valida se o payload é válido da EvolutionAPI."""
    if not isinstance(payload, dict):
        return False
    
    # Verifica se tem campo data ou message
    has_data = "data" in payload
    has_message = "message" in payload or "body" in payload
    
    return has_data or has_message
