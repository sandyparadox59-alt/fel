from telethon import events
from config import OWNER_ID

@events.register(events.NewMessage(outgoing=True, pattern=r"\.owner"))
async def owner_cmd(event):
    await event.respond(f"👑 **Owner ID:** `{OWNER_ID}`")
