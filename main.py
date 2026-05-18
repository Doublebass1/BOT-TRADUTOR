import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from deep_translator import GoogleTranslator

load_dotenv()

API_ID     = int(os.getenv("API_ID"))
API_HASH   = os.getenv("API_HASH")
SESSION    = os.getenv("SESSION_STRING")
SOURCE     = int(os.getenv("SOURCE_GROUP"))
TARGET     = int(os.getenv("TARGET_GROUP"))
TOPIC      = int(os.getenv("TARGET_TOPIC"))

client     = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
translator = GoogleTranslator(source="iw", target="pt")

@client.on(events.NewMessage(chats=SOURCE))
async def handler(event):
    msg  = event.message
    text = msg.text or msg.caption

    if not text or not text.strip():
        return

    try:
        translated = translator.translate(text)
    except Exception as e:
        translated = f"[Erro na tradução: {e}]"

    sender   = await event.get_sender()
    name     = getattr(sender, "first_name", "") or ""
    last     = getattr(sender, "last_name", "") or ""
    fullname = f"{name} {last}".strip() or "Desconhecido"

    output = (
        f"🇮🇱 *{fullname}*\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"{translated}"
    )

    await client.send_message(
        TARGET,
        output,
        parse_mode="markdown",
        reply_to=TOPIC
    )

async def main():
    await client.start()
    print("✅ Tradutor ativo — Israel → seu tópico")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
