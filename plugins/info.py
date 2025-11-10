from telethon import events
import aiohttp
import os

async def get_entity_info(entity):
    """Ambil info user/group dalam HTML"""
    info = []
    if hasattr(entity, "first_name") or hasattr(entity, "last_name"):
        full_name = f"{getattr(entity, 'first_name', '') or ''} {getattr(entity, 'last_name', '') or ''}".strip()
        info.append(f"👤 <b>Full Name:</b> {full_name if full_name else '-'}")
    if hasattr(entity, "username") and entity.username:
        info.append(f"🌐 <b>Username:</b> @{entity.username}")
    info.append(f"🆔 <b>ID:</b> <code>{entity.id}</code>")

    tipe = "🙋‍♂️ <b>Tipe:</b> User"
    if getattr(entity, "bot", False):
        tipe = "🤖 <b>Tipe:</b> Bot"
    elif getattr(entity, "gigagroup", False):
        tipe = "👥 <b>Tipe:</b> Supergroup"
    elif getattr(entity, "megagroup", False):
        tipe = "👥 <b>Tipe:</b> Group"
    elif getattr(entity, "broadcast", False):
        tipe = "📢 <b>Tipe:</b> Channel"
    info.append(tipe)

    if getattr(entity, "verified", False):
        info.append("✅ <b>Terverifikasi:</b> Ya")
    if getattr(entity, "scam", False):
        info.append("🚫 <b>Status:</b> Scam")
    if getattr(entity, "fake", False):
        info.append("⚠️ <b>Status:</b> Fake")

    if hasattr(entity, "title") and entity.title:
        info.append(f"🏷️ <b>Nama Grup:</b> {entity.title}")
    if hasattr(entity, "about") and entity.about:
        desc_preview = entity.about.strip()
        if len(desc_preview) > 400:
            desc_preview = desc_preview[:400] + "..."
        info.append(f"📝 <b>Deskripsi:</b>\n<blockquote>{desc_preview}</blockquote>")

    return "\n".join(info)

def setup(client, db, logger):
    @client.on(events.NewMessage(outgoing=True))
    async def handler(event):
        try:
            cmd = getattr(event, "_command", "").lower()
            if cmd in ["id", "cekid"]:
                if event.is_reply:
                    reply = await event.get_reply_message()
                    user = await reply.get_sender()
                    data = await get_entity_info(user)
                    await event.respond(f"<b>📋 Data User (Reply):</b>\n<blockquote>{data}</blockquote>", parse_mode="html")
                else:
                    sender = await event.get_sender()
                    data = await get_entity_info(sender)
                    await event.respond(f"<b>📋 Data Kamu:</b>\n<blockquote>{data}</blockquote>", parse_mode="html")

            elif cmd in ["idgc", "cekidgc"]:
                if event.is_reply:
                    reply = await event.get_reply_message()
                    user = await reply.get_sender()
                    data = await get_entity_info(user)
                    await event.respond(f"<b>📋 Data User (Reply):</b>\n<blockquote>{data}</blockquote>", parse_mode="html")
                else:
                    chat = await event.get_chat()
                    data = await get_entity_info(chat)
                    await event.respond(f"<b>📋 Data Grup:</b>\n<blockquote>{data}</blockquote>", parse_mode="html")

            elif cmd == "tourl":
                if not event.is_reply:
                    await event.respond("⚠️ Reply pesan berisi file untuk diupload!")
                    return
                reply = await event.get_reply_message()
                file_path = None
                try:
                    file_path = await reply.download_media()
                    if not file_path:
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
                                    await event.respond(f"❌ Upload gagal. Response: {result}")
                finally:
                    if file_path and os.path.exists(file_path):
                        os.remove(file_path)

        except Exception as e:
            logger.error(f"Plugin info.py error: {e}")

    return [handler]
