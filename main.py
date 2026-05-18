import os
import asyncio
from fastapi import FastAPI
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")

app = FastAPI()
client = TelegramClient(StringSession(), API_ID, API_HASH)

@app.on_event("startup")
async def startup():
    await client.connect()
    await client.send_code_request(PHONE)

@app.get("/code/{code}")
async def set_code(code: str):
    await client.sign_in(PHONE, code)
    session = client.session.save()
    return {"session": session}
