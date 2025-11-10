from telethon import events

def setup(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.menu"))
    async def menu_handler(event):
        text = (
            "**📜 MENU USERBOT TELEGRAM 📜**\n\n"
            "`.menu` — Tampilkan menu ini\n"
            "`.id` — Lihat ID kamu atau grup\n"
            "`.ping` — Tes kecepatan respon\n"
            "`.owner` — Info owner bot\n"
        )
        await event.respond(text)
