import asyncio
from pyrogram import Client, filters, enums
from info import ADMINS

@Client.on_message(filters.command("deletelast"))
async def delete_last_messages(client, message):
    if message.chat.type not in (enums.ChatType.SUPERGROUP, enums.ChatType.CHANNEL):
        await message.reply_text("This command is only for groups or supergroups.")
        return

    is_admin = message.from_user.id in ADMINS  # Check if the user is an admin
    if not is_admin:
        await message.reply_text("This command is only for admins.")
        return

    status_message = await message.reply_text("Deleting Messages...", quote=True)
    await message.delete()

    message_ids = []
    count_deletions = 0

    if message.reply_to_message:
        for a_s_message_id in range(message.reply_to_message.message_id, message.message_id):
            message_ids.append(a_s_message_id)
            if len(message_ids) == 100:
                await client.delete_messages(
                    chat_id=message.chat.id,
                    message_ids=message_ids,
                    revoke=True
                )
                count_deletions += len(message_ids)
                message_ids = []

        if len(message_ids) > 0:
            await client.delete_messages(
                chat_id=message.chat.id,
                message_ids=message_ids,
                revoke=True
            )
            count_deletions += len(message_ids)

    await status_message.edit_text(f"Deleted {count_deletions} messages")
    await asyncio.sleep(5)
    await status_message.delete()

