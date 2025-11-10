import os
import sys
import importlib
import asyncio
from telethon import TelegramClient, events
from colorama import Fore, Style
from config import API_ID, API_HASH, SESSION, OWNER_ID

# === Inisialisasi client ===
SESSION_PATH = os.path.join("..", SESSION)
client = TelegramClient(SESSION_PATH, API_ID, API_HASH)

# === Fungsi memuat plugin ===
def load_plugins():
    print(Fore.CYAN + "\n🔌 Memuat plugin...")
    plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
    for filename in os.listdir(plugins_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            name = filename[:-3]
            try:
                # Hapus cache modul dulu
                if f"plugins.{name}" in sys.modules:
                    importlib.reload(sys.modules[f"plugins.{name}"])
                else:
                    importlib.import_module(f"plugins.{name}")
                print(Fore.GREEN + f"✅ Plugin '{name}' dimuat")
            except Exception as e:
                print(Fore.RED + f"❌ Gagal memuat '{name}': {e}")
    print(Style.RESET_ALL)

# === Fungsi reload otomatis ===
async def watch_plugins():
    last_mtime = {}
    plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
    while True:
        for filename in os.listdir(plugins_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                filepath = os.path.join(plugins_dir, filename)
                mtime = os.path.getmtime(filepath)
                if filename not in last_mtime:
                    last_mtime[filename] = mtime
                elif mtime != last_mtime[filename]:
                    print(Fore.YELLOW + f"♻️ Reload plugin '{filename}' karena ada perubahan...")
                    modulename = f"plugins.{filename[:-3]}"
                    try:
                        importlib.reload(sys.modules[modulename])
                        print(Fore.GREEN + f"✅ Reload sukses: {filename}")
                    except Exception as e:
                        print(Fore.RED + f"❌ Reload gagal: {e}")
                    last_mtime[filename] = mtime
        await asyncio.sleep(3)

# === Log semua pesan masuk/keluar ===
@client.on(events.NewMessage)
async def logger(event):
    sender = await event.get_sender()
    sender_name = sender.first_name if sender else "Unknown"
    chat_title = (await event.get_chat()).title if event.is_group else "Private"
    print(
        Fore.MAGENTA
        + f"[MSG] {sender_name} ({chat_title}) -> {event.text}"
        + Style.RESET_ALL
    )

# === HELP bawaan ===
@client.on(events.NewMessage(outgoing=True, pattern=r"\.help"))
async def help_cmd(event):
    text = (
        "**📜 MENU USERBOT TELEGRAM 📜**\n\n"
        "`.help` — Tampilkan menu ini\n"
        "`.menu` — Daftar plugin aktif\n"
        "`.ping` — Tes kecepatan respon\n"
        "`.id` — Lihat ID user/chat\n"
        "`.owner` — Info pemilik bot\n"
        "\nTambah plugin lain di folder `plugins/`"
    )
    await event.respond(text)

# === Menampilkan daftar plugin aktif ===
@client.on(events.NewMessage(outgoing=True, pattern=r"\.menu"))
async def menu_cmd(event):
    plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
    plugins = [f[:-3] for f in os.listdir(plugins_dir) if f.endswith(".py") and f != "__init__.py"]
    text = "**🔌 Plugin aktif:**\n" + "\n".join(f"• `{p}`" for p in plugins)
    await event.respond(text)

# === Start userbot ===
async def main():
    print(Fore.YELLOW + "🚀 Menjalankan Userbot Telegram...")
    load_plugins()
    await client.start()
    print(Fore.GREEN + "✅ Userbot aktif! Ketik `.help` di Telegram.")
    asyncio.create_task(watch_plugins())
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
