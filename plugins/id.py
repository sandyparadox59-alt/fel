from telethon import events
import time

def setup(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.ping"))
    async def ping(event):
        start = time.time()
        msg = await event.respond("🏓 Pong...")
        end = time.time()
        await msg.edit(f"🏓 Pong!\n⏱️ {round((end - start)*1000)} ms")
