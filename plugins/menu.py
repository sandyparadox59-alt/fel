from telethon import events

@events.register(events.NewMessage(outgoing=True, pattern=r"\.menu"))
async def menu_cmd(event):
    text = "**📦 Plugin Aktif:**\n"
    text += "• menu\n• ping\n• id\n• owner\n"
    await event.respond(text)
