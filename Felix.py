import os
import asyncio
from telethon import TelegramClient, events
from colorama import Fore, Style
from config import API_ID, API_HASH, SESSION, OWNER_ID

SESSION_PATH = os.path.join("..", SESSION)

# === Inisialisasi client ===
client = TelegramClient(SESSION_PATH, API_ID, API_HASH)
RESELLERS = [1234567890, 987654321]  # ID Telegram reseller

# === Logger semua pesan ===
@client.on(events.NewMessage)
async def logger(event):
    sender = await event.get_sender()
    name = sender.first_name if sender else "Unknown"
    chat = await event.get_chat()
    chat_name = getattr(chat, "title", "Private")
    print(Fore.MAGENTA + f"[{chat_name}] {name}: {event.text}" + Style.RESET_ALL)

# === HELP ===
@client.on(events.NewMessage(outgoing=True, pattern=r"\.help"))
async def help_handler(event):
    text = (
        "**📜 MENU USERBOT TELEGRAM 📜**\n\n"
        "`.help` — Menampilkan menu bantuan\n"
        "`.ping` — Tes kecepatan respon\n"
        "`.id` — Menampilkan ID pengguna/chat\n"
        "`.teruskan` / `.fw` — Teruskan pesan ke semua grup\n"
        "\nUserbot sederhana tanpa plugin ✅"
    )
    await event.respond(text)

# === FORWARD PESAN KE SEMUA GRUP ===
@client.on(events.NewMessage(outgoing=True, pattern=r"\.(teruskan|fw)"))
async def forward_all(event):
    sender = await event.get_sender()
    sender_id = sender.id

    # === Validasi: hanya owner & reseller ===
    if sender_id != OWNER_ID and sender_id not in RESELLERS:
        await event.reply("🚫 Hanya owner atau reseller yang bisa menggunakan perintah ini.")
        return

    # === Cek apakah reply pesan ===
    reply = await event.get_reply_message()
    if not reply:
        await event.reply("⚠️ Harap reply pesan yang ingin diteruskan!")
        return

    # === Ambil semua grup di mana userbot bergabung ===
    print("📋 Mengambil daftar grup...")
    dialogs = await client.get_dialogs()
    groups = [d for d in dialogs if d.is_group or d.is_channel]
    print(f"✅ Ditemukan {len(groups)} grup untuk forward pesan.")

    sukses = 0
    gagal = 0

    for group in groups:
        try:
            if reply.media:
                await client.send_file(group.id, reply.media, caption=reply.text or "")
            else:
                await client.send_message(group.id, reply.text or " ")
            print(f"✅ Dikirim ke grup: {group.name}")
            sukses += 1
        except Exception as e:
            print(f"❌ Gagal kirim ke {group.name}: {e}")
            gagal += 1

    await event.reply(
        f"📤 Pesan berhasil diteruskan!\n"
        f"✅ Berhasil: {sukses}\n"
        f"❌ Gagal: {gagal}"
    )

# === PING ===
@client.on(events.NewMessage(outgoing=True, pattern=r"\.ping"))
async def ping_handler(event):
    start = event.message.date
    msg = await event.respond("🏓 Pong...")
    end = msg.date
    latency = (end - start).total_seconds() * 1000
    await msg.edit(f"🏓 Pong! `{latency:.2f} ms`")

# === ID ===
@client.on(events.NewMessage(outgoing=True, pattern=r"\.id"))
async def id_handler(event):
    if event.is_reply:
        replied = await event.get_reply_message()
        user_id = replied.sender_id
        await event.respond(f"🆔 **ID dari pesan yang direply:** `{user_id}`")
    else:
        chat_id = event.chat_id
        await event.respond(f"🆔 **Chat ID ini:** `{chat_id}`")

# === MAIN ===
async def main():
    print(Fore.YELLOW + "🚀 Menjalankan Userbot Telegram tanpa plugin...")
    await client.start()
    print(Fore.GREEN + "✅ Userbot aktif! Ketik `.help` di Telegram.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
