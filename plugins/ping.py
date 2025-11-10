from telethon import events

def setup(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.owner"))
    async def owner(event):
        await event.respond("👑 Owner: @GlobalBotzXD")
