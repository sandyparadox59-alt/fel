from telethon import events
import time

@events.register(events.NewMessage(outgoing=True, pattern=r"\.ping"))
async def ping_cmd(event):
    start = time.time()
    msg = await event.respond("🏓 Pong!")
    end = time.time() - start
    await msg.edit(f"🏓 Pong! `{round(end * 1000)}ms`")
