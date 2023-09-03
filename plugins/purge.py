import asyncio
from pyrogram import Client, filters
from info import ADMINS  # Assuming you have a file named 'info.py' with the ADMINS list.

# Define your chat IDs
chat_ids = [-1001912697656]

@Client.on_message(filters.command('purge_all') & filters.user(ADMINS))
async def purge(client, message):
    if message.chat.id not in chat_ids:
        return

    is_admin = message.from_user and message.from_user.id in ADMINS
    if not is_admin:
        return

    # Send a status message indicating the purge is in progress
    status_message = await message.reply_text("Purging...", quote=True)
    await message.delete()

    message_ids = []
    count_deletions = 0

    if message.reply_to_message:
        # Loop through message IDs to be deleted
        for a_message_id in range(message.reply_to_message.message_id, message.message_id):
            message_ids.append(a_message_id)
            if len(message_ids) == 100:
                await client.delete_messages(
                    chat_id=message.chat.id,
                    message_ids=message_ids,
                    revoke=True
                )
                count_deletions += len(message_ids)
                message_ids = []

        # Delete any remaining messages
        if len(message_ids) > 0:
            await client.delete_messages(
                chat_id=message.chat.id,
                message_ids=message_ids,
                revoke=True
            )
            count_deletions += len(message_ids)

    # Edit the status message to indicate the number of deleted messages
    await status_message.edit_text(f"Deleted {count_deletions} messages")
    await asyncio.sleep(5)
    await status_message.delete()
