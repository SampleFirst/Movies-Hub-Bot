import asyncio
from pyrogram import Client, filters, enums
from info import ADMINS

@Client.on_message(filters.command("clean") & (filters.group | filters.channel))
async def clean(client, message):
    if message.chat.type not in ((enums.ChatType.SUPERGROUP, enums.ChatType.CHANNEL)):
        return
    is_admin = message.from_user.id in ADMINS
    if not is_admin:
        return

    status_message = await message.reply_text("Cleaning up...", quote=True)
    await message.delete()

    # Get all message IDs in the chat
    all_messages = await client.get_history(chat_id=message.chat.id, limit=None)
    message_ids = [msg.message_id for msg in all_messages]

    # Delete messages in batches of 100
    count_deletions = 0
    for batch_start in range(0, len(message_ids), 100):
        batch = message_ids[batch_start : batch_start + 100]
        await client.delete_messages(chat_id=message.chat.id, message_ids=batch, revoke=True)
        count_deletions += len(batch)
    
    await status_message.edit_text(f"Deleted {count_deletions} messages")
    await asyncio.sleep(5)
    await status_message.delete()
