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
SOURCE     = int(os.getenv("SOURCE_GROUP"))   # -1001289614360
TARGET     = int(os.getenv("TARGET_GROUP"))   # -1003828699315
TOPIC      = int(os.getenv("TARGET_TOPIC"))   # 1

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
    name     = getattr(sender, "first_name", "Desconhecido") or "Desconhecido"
    username = f"@{sender.username}" if getattr(sender, "username", None) else ""

    output = f"🇮🇱 *{name}* {username}\n\n{translated}"

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