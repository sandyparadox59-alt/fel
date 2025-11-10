from telethon import events

@events.register(events.NewMessage(outgoing=True, pattern=r"\.id"))
async def id_cmd(event):
    chat_id = event.chat_id
    sender = await event.get_sender()
    sender_id = sender.id
    text = f"👤 **User ID:** `{sender_id}`\n💬 **Chat ID:** `{chat_id}`"
    await event.respond(text)
