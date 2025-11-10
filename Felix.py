import os
import sys
import importlib
import asyncio
from telethon import TelegramClient, events
from colorama import Fore, Style
from config import API_ID, API_HASH, SESSION, OWNER_ID

# --- INISIASI CLIENT ---
client = TelegramClient(SESSION, API_ID, API_HASH)

# --- FUNGSI LOAD PLUGIN ---
def load_plugins():
    print(Fore.CYAN + "\n🔌 Memuat plugin...")
    for filename in os.listdir("plugins"):
        if filename.endswith(".py") and filename != "__init__.py":
            name = filename[:-3]
            try:
                module = importlib.import_module(f"plugins.{name}")
                # cari semua event handler yang pakai @events.register
                for attr in dir(module):
                    obj = getattr(module, attr)
                    if hasattr(obj, "handler") and hasattr(obj.handler, "callback"):
                        client.add_event_handler(obj.handler.callback, obj.handler)
                print(Fore.GREEN + f"✅ Plugin '{name}' dimuat")
            except Exception as e:
                print(Fore.RED + f"❌ Gagal memuat '{name}': {e}")
    print(Style.RESET_ALL)

# --- FUNGSI: WATCH PLUGIN (AUTO RELOAD) ---
async def watch_plugins():
    last_mtime = {}
    while True:
        plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
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

# --- HELP DEFAULT ---
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

# --- STARTUP ---
async def main():
    print(Fore.YELLOW + "🚀 Menjalankan Userbot Telegram...")
    load_plugins()
    await client.start()
    print(Fore.GREEN + "✅ Userbot aktif! Ketik `.help` di Telegram.")
    asyncio.create_task(watch_plugins())
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
