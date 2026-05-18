import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient, events
from deep_translator import GoogleTranslator

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")
SOURCE_GROUP = int(os.getenv("SOURCE_GROUP"))
TARGET_GROUP = int(os.getenv("TARGET_GROUP"))

client = TelegramClient("translator_session", API_ID, API_HASH)
translator = GoogleTranslator(source="iw", target="pt")  # iw = hebraico

@client.on(events.NewMessage(chats=SOURCE_GROUP))
async def handler(event):
    msg = event.message
    text = msg.text or msg.caption

    if not text or not text.strip():
        return  # ignora mensagens sem texto (stickers, etc.)

    try:
        translated = translator.translate(text)
    except Exception as e:
        translated = f"[Erro na tradução: {e}]"

    sender = await event.get_sender()
    name = getattr(sender, "first_name", "Desconhecido") or "Desconhecido"
    username = f"@{sender.username}" if getattr(sender, "username", None) else ""

    output = f"🇮🇱 *{name}* {username}\n\n{translated}"

    await client.send_message(TARGET_GROUP, output, parse_mode="markdown")

async def main():
    await client.start(phone=PHONE)
    print("✅ Translator ativo. Monitorando grupo de Israel...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())