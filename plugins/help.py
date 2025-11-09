from telethon import events
from main import client

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.help$"))
async def help_menu(event):
    text = (
        "**📜 MENU USERBOT**\n\n"
        "`.ping` — Tes kecepatan bot\n"
        "`.id` — Cek ID pengguna/chat\n"
        "`.reload` — Reload semua plugin tanpa restart\n"
        "`.help` — Tampilkan menu ini\n"
    )
    await event.respond(text)
