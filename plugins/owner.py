import asyncio
import subprocess
from telethon import events

def setup(client, db, logger, is_owner, is_reseller):
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\$ '))
    async def run_shell(event):
        if not is_owner:
            return

        # Ambil teks setelah simbol $
        command = event.raw_text[2:].strip()
        if not command:
            await event.respond("⚠️ Masukkan perintah bash, contoh:\n`$ ls -la`")
            return

        await event.respond("⏳ Executing...")

        try:
            # Jalankan perintah di shell (bash)
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            out = stdout.decode().strip()
            err = stderr.decode().strip()

            if out:
                # Jika output terlalu panjang, potong
                if len(out) > 4000:
                    out = out[:4000] + "\n... (output terpotong)"
                await event.respond(f"✅ <b>Output:</b>\n<pre>{out}</pre>", parse_mode="html")

            if err:
                if len(err) > 4000:
                    err = err[:4000] + "\n... (stderr terpotong)"
                await event.respond(f"⚠️ <b>Error:</b>\n<pre>{err}</pre>", parse_mode="html")

            if not out and not err:
                await event.respond("✅ Perintah selesai tanpa output.")

        except Exception as e:
            logger.error(f"Exec error: {e}")
            await event.respond(f"❌ Gagal menjalankan perintah:\n`{e}`")

    return [run_shell]
