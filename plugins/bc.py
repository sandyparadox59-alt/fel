from telethon import events
import asyncio

COMMANDS_FORWARD = {
    'bcgc': 'gc',
    'bc': 'user',
    'bcall': 'all'
}

SEND_DELAY = 1.5  # detik

def setup(client, db, logger, is_owner, is_reseller):

    @client.on(events.NewMessage)
    async def handler(event):
        try:
            cmd = getattr(event, "_command", "").lower()
            mode = COMMANDS_FORWARD.get(cmd)
            if not mode:
                return

            sender = await event.get_sender()
            sender_id = sender.id

            # === Validasi: hanya owner & reseller ===
            if not (is_owner(sender_id) or is_reseller(sender_id)):
                await event.reply("🚫 Hanya owner atau reseller yang bisa menggunakan perintah ini.")
                return

            # === Cek apakah reply pesan ===
            reply = await event.get_reply_message()
            if not reply:
                await event.reply("⚠️ Harap reply pesan yang ingin diteruskan!")
                return

            sukses = 0
            gagal = 0
            targets = []

            dialogs = await client.get_dialogs()

            if mode == 'gc':
                targets = [d for d in dialogs if d.is_group or d.is_channel]

            elif mode == 'user':
                if event.is_private:
                    targets = [d for d in dialogs if d.is_user and not d.entity.bot]
                else:
                    chat = await event.get_chat()
                    members = await client.get_participants(chat)
                    targets = [m for m in members if not m.bot]

            elif mode == 'all':
                groups = [d for d in dialogs if d.is_group or d.is_channel]
                users = [d for d in dialogs if d.is_user and not d.entity.bot]
                targets = users + groups
                for grp in groups:
                    try:
                        members = await client.get_participants(grp)
                        targets += [m for m in members if not m.bot]
                    except Exception as e:
                        logger.error(f"Gagal ambil anggota grup {getattr(grp, 'name', grp.id)}: {e}")

            # === Kirim / forward pesan ===
            for chat in targets:
                try:
                    await client.forward_messages(chat.id, reply)
                    sukses += 1
                    await asyncio.sleep(SEND_DELAY)
                except Exception as e:
                    logger.error(f"❌ Gagal kirim ke {getattr(chat, 'title', getattr(chat, 'id', 'Unknown'))}: {e}")
                    gagal += 1

            await event.reply(
                f"📤 Pesan berhasil diteruskan!\n"
                f"✅ Berhasil: {sukses}\n"
                f"❌ Gagal: {gagal}"
            )

        except Exception as e:
            logger.error(f"Gagal menjalankan plugin forward: {e}")
