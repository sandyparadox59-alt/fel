from telethon import events
import aiohttp
import os
import time

async def upload_catbox(file_path):
    async with aiohttp.ClientSession() as session:
        with open(file_path, "rb") as f:
            form = aiohttp.FormData()
            form.add_field("reqtype", "fileupload")
            form.add_field("fileToUpload", f)
            async with session.post("https://catbox.moe/user/api.php", data=form) as res:
                return await res.text()

def setup(client, db, logger):
    @client.on(events.NewMessage(outgoing=True))
    async def handler(event):
        try:
            cmd = getattr(event, "_command", "").lower()

            # -------------------------
            # PING
            # -------------------------
            if cmd == "ping":
                start = time.time()
                msg = await event.respond("🏓 Pong...")
                end = time.time()
                latency = (end - start) * 1000
                await msg.edit(f"🏓 Pong! `{latency:.2f} ms`")

            # -------------------------
            # TOURl
            # -------------------------
            elif cmd == "tourl":
                if not event.is_reply:
                    await event.respond("⚠️ Reply pesan berisi file untuk diupload!")
                    return
                reply = await event.get_reply_message()
                file_path = None
                try:
                    file_path = await reply.download_media()
                    if not file_path:
                        try:
                        await event.respond("❌ Gagal mendownload file.")
                        return
                    async with aiohttp.ClientSession() as session:
                        with open(file_path, "rb") as f:
                            data = aiohttp.FormData()
                            data.add_field('file', f)
                            async with session.post("https://file.io", data=data) as resp:
                                result = await resp.json()
                                url = result.get("link") or result.get("success", False)
                                if url:
                                    await event.respond(f"✅ File berhasil diupload:\n{url}")
                                else:
                                urlx = await upload_catbox(file)
                               if urlx:
                                    await event.respond(f"✅ File berhasil diupload:\n{urlx}")
                                 else:
                                    await event.respond(f"❌ Upload gagal. Response: {urlx}")
                finally:
                    if file_path and os.path.exists(file_path):
                        os.remove(file_path)

        except Exception as e:
            logger.error(f"Plugin misc.py error: {e}")

    return [handler]
