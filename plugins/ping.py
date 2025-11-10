from telethon import events
import time

@events.register(events.NewMessage(outgoing=True, pattern=r"\.ping"))
async def ping(event):
    start = time.time()
    msg = await event.respond("🏓 Pong!")
    end = time.time()
    await msg.edit(f"🏓 Pong! `{(end - start)*1000:.1f} ms`")
