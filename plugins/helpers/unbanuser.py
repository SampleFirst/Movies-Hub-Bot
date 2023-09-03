from pyrogram import Client, filters

@Client.on_message(filters.private & filters.command("unban_user"))
async def unban_user_pm(_, message):
    try:
        # Parse the command in the format "/unban chat_id user_id"
        _, chat_id, user_id = message.text.split()
        chat_id = int(chat_id)
        user_id = int(user_id)
    except ValueError:
        await message.reply_text("Invalid command format. Please use /unban_user chat_id user_id")
        return
    
    is_admin = message.from_user and message.from_user.id in ADMINS
    if not is_admin:
        await message.reply_text("You are not authorized to perform this action.")
        return
    
    try:
        await Client.get_chat(chat_id).unban_member(user_id=user_id)
    except Exception as error:
        await message.reply_text(str(error))
    else:
        await message.reply_text("User has been unbanned in the specified chat.")
