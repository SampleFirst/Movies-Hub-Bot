import asyncio
from pyrogram import Client, filters
from info import ADMINS 

@Client.on_message(filters.command("purge") & filters.private)
async def purge_command(client, message):
    if message.from_user.id not in ADMINS:
        await message.reply_text("You are not authorized to use this command.")
        return

    try:
        chat_id = int(message.command[1])
    except (ValueError, IndexError):
        await message.reply_text("Please provide a valid chat ID.")
        return

    async def delete_messages(chat_id, message_ids):
        await client.delete_messages(
            chat_id=chat_id,
            message_ids=message_ids,
            revoke=True
        )

    async with client.conversation(chat_id) as conv:
        await conv.send_message("Executing purge command...")
        async for msg in conv.iter_history():
            await delete_messages(chat_id, [msg.message_id])
            await asyncio.sleep(1)  # To avoid rate limits

        await conv.send_message("All messages in the chat have been deleted.")
