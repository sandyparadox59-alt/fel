from telethon import events

def setup(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.id"))
    async def id(event):
        reply = await event.get_reply_message()
        if reply:
            await event.respond(f"🆔 ID Reply: `{reply.sender_id}`")
        else:
            await event.respond(f"🆔 ID Kamu: `{event.sender_id}`\n💬 Chat ID: `{event.chat_id}`")
