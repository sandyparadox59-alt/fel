from telethon import events
from urllib.parse import urlencode
import filetype
import aiohttp
import os
import time
import requests


# === UPLOAD FILE KE CATBOX ===
async def upload_catbox(file_path):
    async with aiohttp.ClientSession() as session:
        with open(file_path, "rb") as f:
            form = aiohttp.FormData()
            form.add_field("reqtype", "fileupload")
            form.add_field("fileToUpload", f)
            async with session.post("https://catbox.moe/user/api.php", data=form) as res:
                return await res.text()


def upload_to_pxpic(buffer: bytes):
    """Upload file ke Pxpic dan kembalikan URL hasil upload."""
    kind = filetype.guess(buffer)
    ext = kind.extension if kind else "png"
    mime = kind.mime if kind else "image/png"
    file_name = f"{int(time.time() * 1000)}.{ext}"

    # === Minta signed URL ===
    resp = requests.post(
        "https://pxpic.com/getSignedUrl",
        json={"folder": "uploads", "fileName": file_name},
        headers={"Content-Type": "application/json"}
    )
    resp.raise_for_status()
    res_json = resp.json()

    # === Patch perbedaan struktur ===
    if "data" in res_json:
        presigned = res_json["data"]
    else:
        presigned = res_json  # fix: sesuai hasil di error kamu

    # Pastikan URL tersedia
    presigned_url = presigned.get("presignedUrl")
    if not presigned_url:
        raise ValueError(f"[Pxpic ERROR] Invalid response structure: {res_json}")

    # === Upload gambar ===
    upload_resp = requests.put(presigned_url, data=buffer, headers={"Content-Type": mime})
    upload_resp.raise_for_status()

    return f"https://files.fotoenhancer.com/uploads/{file_name}"



# === GUNAKAN AI FUNCTION ===
def create_pxpic_image(buffer: bytes, type_: str = "removebg"):
    """Gunakan AI Pxpic untuk proses gambar (removebg, upscale, dsb)."""
    try:
        url = upload_to_pxpic(buffer)
        if not url:
            print("[Pxpic ERROR] Upload gagal, URL kosong.")
            return None

        payload = {
            "imageUrl": url,
            "targetFormat": "png",
            "needCompress": "no",
            "imageQuality": "100",
            "compressLevel": "6",
            "fileOriginalExtension": "png",
            "aiFunction": type_,
            "upscalingLevel": ""
        }

        data = urlencode(payload)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        resp = requests.post(
            "https://pxpic.com/callAiFunction",
            data=data,
            headers=headers,
            timeout=30
        )
        resp.raise_for_status()
        result = resp.json()

        if "resultImageUrl" in result:
            return result["resultImageUrl"]

        print("[Pxpic ERROR] Response tidak berisi resultImageUrl:", result)
        return None

    except Exception as e:
        print(f"[Pxpic ERROR] {e}")
        return None


# === PLUGIN SETUP ===
def setup(client, db, logger, is_owner, is_reseller):
    @client.on(events.NewMessage(outgoing=True))
    async def handler(event):
        try:
            cmd = event.raw_text.strip().split()[0].lower().replace(".", "")

            # === PING ===
            if cmd == "ping":
                start = time.time()
                msg = await event.respond("🏓 Pong...")
                end = time.time()
                await msg.edit(f"🏓 Pong! `{(end - start) * 1000:.2f} ms`")

            # === TO URL ===
            elif cmd == "tourl":
                if not event.is_reply:
                    return await event.respond("⚠️ Reply pesan berisi file untuk diupload!")

                reply = await event.get_reply_message()
                file_path = await reply.download_media()
                if not file_path:
                    return await event.respond("❌ Gagal mendownload file.")

                try:
                    url = await upload_catbox(file_path)
                    if url and url.startswith("http"):
                        await event.respond(f"✅ File berhasil diupload ke Catbox:\n{url}")
                    else:
                        with open(file_path, "rb") as f:
                            buffer = f.read()
                        pxurl = upload_to_pxpic(buffer)
                        if pxurl:
                            await event.respond(f"✅ File berhasil diupload ke Pxpic:\n{pxurl}")
                        else:
                            await event.respond("❌ Upload gagal ke Pxpic.")
                finally:
                    if os.path.exists(file_path):
                        os.remove(file_path)

            # === REMOVE BACKGROUND / HD ===
            elif cmd in ["removebg", "hd", "remini"]:
                mode = "removebg" if cmd == "removebg" else "upscale"
                action_text = "menghapus background" if mode == "removebg" else "memperjelas (HD)"

                if not event.is_reply:
                    return await event.respond(f"⚠️ Reply gambar untuk {action_text}!")

                reply = await event.get_reply_message()
                file_path = await reply.download_media()
                if not file_path:
                    return await event.respond("❌ Gagal mendownload gambar.")

                try:
                    with open(file_path, "rb") as f:
                        buffer = f.read()

                    await event.respond(f"⏳ Sedang {action_text} gambar...")

                    result_url = create_pxpic_image(buffer, type_=mode)
                    if result_url:
                        await event.respond(
                            f"✅ Gambar berhasil {action_text}!\n{result_url}"
                        )
                    else:
                        await event.respond(f"❌ Gagal {action_text}. Coba lagi nanti.")
                finally:
                    if os.path.exists(file_path):
                        os.remove(file_path)

        except Exception as e:
            logger.error(f"[AI Plugin Error] {e}")
            await event.respond(f"❌ Terjadi error:\n`{e}`")

    return [handler]
