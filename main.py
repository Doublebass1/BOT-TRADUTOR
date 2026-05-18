import os
import asyncio
import anthropic
from datetime import datetime
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from deep_translator import GoogleTranslator

load_dotenv()

API_ID      = int(os.getenv("API_ID"))
API_HASH    = os.getenv("API_HASH")
SESSION     = os.getenv("SESSION_STRING")
SOURCE      = int(os.getenv("SOURCE_GROUP"))
TARGET      = int(os.getenv("TARGET_GROUP"))
TOPIC       = int(os.getenv("TARGET_TOPIC"))
CLAUDE_KEY  = os.getenv("ANTHROPIC_API_KEY")

client      = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
claude      = anthropic.Anthropic(api_key=CLAUDE_KEY)

def detect_and_translate(text: str) -> str:
    """Detecta idioma automaticamente e traduz para português."""
    try:
        translated = GoogleTranslator(source="auto", target="pt").translate(text)
        return translated
    except Exception as e:
        return f"[Erro na tradução: {e}]"

def classify_emergency(text: str, translated: str) -> dict:
    """Usa Claude para classificar urgência da mensagem."""
    try:
        response = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": f"""Analise esta mensagem de um grupo de notícias do Oriente Médio e classifique a urgência.

Texto original: {text}
Tradução: {translated}

Responda APENAS em JSON neste formato exato:
{{
  "nivel": "NORMAL" ou "IMPORTANTE" ou "EMERGENCIAL",
  "motivo": "uma frase curta explicando o nível"
}}

EMERGENCIAL = eventos que afetam múltiplos países ou o mundo: guerra declarada oficialmente, ataque nuclear/químico/biológico confirmado, colapso de governo com violência em massa, ataque terrorista com centenas de vítimas confirmadas, catástrofe natural de escala global.

IMPORTANTE = conflito localizado, ataque militar pontual, mortes confirmadas, tensão diplomática grave.

NORMAL = opinião, discussão, notícia cotidiana, rumor, política interna."""
            }]
        )
        import json
        raw = response.content[0].text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception:
        return {"nivel": "NORMAL", "motivo": ""}

def format_time() -> str:
    now = datetime.now()
    return now.strftime("%H:%M · %d/%m/%Y")

@client.on(events.NewMessage(chats=SOURCE))
async def handler(event):
    msg  = event.message
    text = msg.text or msg.caption or ""
    has_media = msg.media is not None

    if not text.strip() and not has_media:
        return

    # Traduz o texto se houver
    translated = detect_and_translate(text) if text.strip() else ""

    # Classifica urgência via Claude
    nivel_info = {"nivel": "NORMAL", "motivo": ""}
    if text.strip():
        nivel_info = classify_emergency(text, translated)

    nivel = nivel_info.get("nivel", "NORMAL")

    # Monta cabeçalho do remetente
    sender   = await event.get_sender()
    name     = getattr(sender, "first_name", "") or ""
    last     = getattr(sender, "last_name", "") or ""
    fullname = f"{name} {last}".strip() or "Desconhecido"
    horario  = format_time()

    # Define emoji e separador por nível
    if nivel == "EMERGENCIAL":
        emoji_nivel = "🚨"
        separador   = "🔴🔴🔴🔴🔴🔴🔴🔴"
    elif nivel == "IMPORTANTE":
        emoji_nivel = "⚠️"
        separador   = "▬▬▬▬▬▬▬▬▬▬▬▬"
    else:
        emoji_nivel = "🇮🇱"
        separador   = "┄┄┄┄┄┄┄┄┄┄┄┄"

    # Monta mensagem principal
    caption = (
        f"{emoji_nivel} *{fullname}*  `{horario}`\n"
        f"{separador}\n"
        f"{translated if translated else '_(sem texto)_'}"
    )

    # Envia mídia com legenda ou só texto
    if has_media:
        await client.send_file(
            TARGET,
            msg.media,
            caption=caption,
            parse_mode="markdown",
            reply_to=TOPIC
        )
    else:
        await client.send_message(
            TARGET,
            caption,
            parse_mode="markdown",
            reply_to=TOPIC
        )

    # Alerta separado para emergências
    if nivel == "EMERGENCIAL":
        motivo = nivel_info.get("motivo", "")
        alerta = (
            f"🚨🚨🚨 *ALERTA EMERGENCIAL* 🚨🚨🚨\n\n"
            f"📍 *{motivo}*\n\n"
            f"⬆️ Veja a mensagem acima para detalhes.\n\n"
            f"@everyone"
        )
        await client.send_message(
            TARGET,
            alerta,
            parse_mode="markdown",
            reply_to=TOPIC
        )

async def main():
    await client.start()
    print("✅ Tradutor ativo — Israel → seu tópico")
    print("🤖 Claude AI ativado para classificação de emergências")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
