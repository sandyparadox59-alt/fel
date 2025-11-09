from telethon import events
from main import client

@client.on(events.NewMessage(outgoing=True, pattern=r"\.id"))
async def get_id(event):
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        await event.respond(f"👤 ID Pengguna: `{reply_msg.sender_id}`")
    else:
        await event.respond(f"💬 ID Chat: `{event.chat_id}`")
