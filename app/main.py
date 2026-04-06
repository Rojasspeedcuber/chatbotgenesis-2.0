from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Dict

from app.config import settings
from app.db.mysql import get_db, test_connection
from app.agents.bible_agent import BibleAgent
from app.tools.webhook_tools import (
    extract_incoming_message,
    build_whatsapp_response,
    validate_evolution_payload,
    extract_sender_info,
)
from app.tools.formatting_tools import split_long_message

app = FastAPI(
    title=settings.APP_NAME,
    description="Bot Bíblico com integração WhatsApp via EvolutionAPI",
    version="1.0.0"
)


class MessageRequest(BaseModel):
    message: str
    version: str = "NVI"


class WebhookPayload(BaseModel):
    # Aceita qualquer estrutura para flexibilidade com EvolutionAPI
    class Config:
        extra = "allow"


@app.on_event("startup")
async def startup_event():
    """Verifica conexão com banco na inicialização."""
    if test_connection():
        print("✅ Conexão com MySQL estabelecida")
    else:
        print("❌ Falha na conexão com MySQL - verifique as env vars")


@app.get("/")
def health_check():
    """Health check básico."""
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "version": "1.0.0"
    }


@app.get("/health")
def detailed_health():
    """Health check com banco."""
    db_ok = test_connection()
    return {
        "status": "healthy" if db_ok else "unhealthy",
        "database": "connected" if db_ok else "disconnected",
        "app": settings.APP_NAME
    }


@app.post("/chat")
def chat_endpoint(
    payload: MessageRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint direto para testes.
    Recebe mensagem e retorna resposta do agente.
    """
    try:
        agent = BibleAgent(db, default_version=payload.version)
        response_text = agent.handle_message(payload.message)
        
        return build_whatsapp_response(response_text)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/evolution")
def evolution_webhook(
    payload: Dict,
    db: Session = Depends(get_db)
):
    """
    Webhook para EvolutionAPI.
    Recebe payload do WhatsApp, processa e retorna resposta.
    """
    try:
        # Valida payload
        if not validate_evolution_payload(payload):
            return {"status": "ignored", "reason": "invalid_payload"}
        
        # Extrai dados
        incoming_msg = extract_incoming_message(payload)
        sender_info = extract_sender_info(payload)
        
        if not incoming_msg:
            return {"status": "ignored", "reason": "empty_message"}
        
        # Processa com o agente
        agent = BibleAgent(db, default_version=settings.DEFAULT_BIBLE_VERSION)
        response_text = agent.handle_message(incoming_msg)
        
        # Se a mensagem for muito longa, pega só a primeira parte
        # (WhatsApp tem limite, e a EvolutionAPI gerencia múltiplas mensagens se necessário)
        parts = split_long_message(response_text)
        final_response = parts[0] if parts else "Desculpe, não consegui processar sua mensagem."
        
        return build_whatsapp_response(final_response)
    
    except Exception as e:
        print(f"Erro no webhook: {e}")
        return {
            "message": "Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente."
        }


@app.post("/webhook/test")
def test_webhook(payload: Dict):
    """
    Endpoint para testar o formato do webhook sem processar.
    Útil para debug.
    """
    return {
        "extracted_message": extract_incoming_message(payload),
        "sender": extract_sender_info(payload),
        "valid": validate_evolution_payload(payload),
        "raw_payload": payload
    }
