import os
import importlib
from telethon import TelegramClient, events
from colorama import Fore, Style

# --- KONFIGURASI USERBOT ---
API_ID = 33931529  # ganti dari https://my.telegram.org
API_HASH = "7bdc34f542e3a6eff7558646271e59ec"
SESSION = "userbot"  # nama session file

# --- INISIASI TELETHON ---
client = TelegramClient(SESSION, API_ID, API_HASH)

# --- FUNGSI LOAD PLUGIN ---
def load_plugins():
    print(Fore.CYAN + "\n🔌 Memuat plugin...")
    for filename in os.listdir("plugins"):
        if filename.endswith(".py") and filename != "__init__.py":
            name = filename[:-3]
            importlib.import_module(f"plugins.{name}")
            print(Fore.GREEN + f"✅ Plugin '{name}' dimuat")
    print(Style.RESET_ALL)

# --- COMMAND HELP DEFAULT ---
@client.on(events.NewMessage(outgoing=True, pattern=r"\.help"))
async def help_cmd(event):
    text = (
        "**📜 MENU USERBOT TELEGRAM 📜**\n\n"
        "`.help` — Tampilkan menu ini\n"
        "`.id` — Lihat ID user/chat\n"
        "\nTambah plugin lain di folder `plugins/`"
    )
    await event.respond(text)

print(Fore.YELLOW + "🚀 Menjalankan Userbot Telegram...")
load_plugins()

client.start()
print(Fore.GREEN + "✅ Userbot aktif! Ketik `.help` di Telegram.")
client.run_until_disconnected()
