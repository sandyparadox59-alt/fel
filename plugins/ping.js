from telethon import events
from main import client
import time

@client.on(events.NewMessage(outgoing=True, pattern=r"\.ping"))
async def ping(event):
    start = time.time()
    msg = await event.respond("🏓 Pong...")
    end = time.time()
    ms = (end - start) * 1000
    await msg.edit(f"🏓 Pong! `{ms:.2f} ms`")
