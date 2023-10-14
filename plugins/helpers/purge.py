from pyrogram import Client, filters
from pyrogram import types, errors
from info import ADMINS 


@Client.on_message(filters.command("purge") & (filters.group | filters.channel))
async def purge_command(client, message):
    if message.chat.type not in (types.ChatType.SUPERGROUP, types.ChatType.CHANNEL):
        await message.reply("This command is only for Supergroups or channels.")
        return
    
    is_admin = message.from_user.id in ADMINS
    if not is_admin:
        await message.reply("This command is only for admins.")
        return
    
    status_message = await message.reply_text("Deleting messages...", quote=True)
    await message.delete()
    
    message_ids = []
    count_deleted_messages = 0
    
    if message.reply_to_message:
        try:
            async for msg in client.iter_history(message.chat.id, offset_id=message.reply_to_message.message_id, reverse=True):
                message_ids.append(msg.message_id)
                if len(message_ids) == 100:
                    await client.delete_messages(chat_id=message.chat.id, message_ids=message_ids, revoke=True)
                    count_deleted_messages += len(message_ids)
                    message_ids = []
        except errors.FloodWait as e:
            await status_message.edit_text(f"Flood wait: {e.x} seconds. Couldn't delete all messages.")
        
        if len(message_ids) > 0:
            await client.delete_messages(chat_id=message.chat.id, message_ids=message_ids, revoke=True)
            count_deleted_messages += len(message_ids)
    
    await status_message.edit_text(f"Deleted {count_deleted_messages} messages.")
    await status_message.delete()
