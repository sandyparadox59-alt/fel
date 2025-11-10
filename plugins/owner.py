from telethon import events

@events.register(events.NewMessage(outgoing=True, pattern=r"\.id"))
async def id_cmd(event):
    chat = await event.get_chat()
    sender = await event.get_sender()
    await event.respond(f"**Chat ID:** `{chat.id}`\n**User ID:** `{sender.id}`")
