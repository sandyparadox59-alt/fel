import os, importlib
from telethon import TelegramClient, events
from colorama import Fore, Style
from config import api_id, api_hash, session_name

# === INISIASI TELETHON ===
client = TelegramClient(session_name, api_id, api_hash)

# === FUNGSI LOAD SEMUA PLUGINS ===
def load_plugins():
    path = "plugins"
    if not os.path.exists(path):
        os.mkdir(path)
    for file in os.listdir(path):
        if file.endswith(".py") and not file.startswith("__"):
            name = file[:-3]
            try:
                importlib.import_module(f"{path}.{name}")
                print(Fore.GREEN + f"✅ Loaded plugin: {name}")
            except Exception as e:
                print(Fore.RED + f"❌ Failed to load {name}: {e}")
    print(Style.RESET_ALL)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.reload$"))
async def reload_plugins(event):
    await event.respond("♻️ Reloading plugins...")
    for name in list(importlib.sys.modules.keys()):
        if name.startswith("plugins."):
            importlib.reload(importlib.import_module(name))
    await event.respond("✅ Plugins reloaded!")

async def main():
    print(Fore.YELLOW + "🚀 Starting Telegram Userbot...")
    await client.start()  # ⬅️ Tidak minta OTP lagi kalau sudah pernah login
    load_plugins()
    print(Fore.CYAN + "✅ Userbot aktif! Ketik `.help` di Telegram.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
