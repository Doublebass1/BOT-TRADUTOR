from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv
import os

load_dotenv()

with TelegramClient(StringSession(), int(os.getenv("API_ID")), os.getenv("API_HASH")) as c:
    c.start(phone=os.getenv("PHONE"))
    print("\n🔑 Copie sua SESSION_STRING abaixo:\n")
    print(c.session.save())