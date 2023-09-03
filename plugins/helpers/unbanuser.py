from pyrogram import Client, filters
from info import *

@Client.on_message(filters.private & filters.command("unban_pm"))
async def unban_user_pm(client, message):
    
    try:
        # Parse the command in the format "/unban_pm user_id"
        _, user_id = message.text.split()
        user_id = int(user_id)
    except ValueError:
        await message.reply_text("Invalid command format. Please use /unban_pm user_id")
        return
    
    is_admin = message.from_user and message.from_user.id in ADMINS
    if not is_admin:
        await message.reply_text("You are not authorized to perform this action.")
        return
    
    chat_id = -1001912697656  # Replace with the desired chat_id
    
    try:
        chat = await client.get_chat(chat_id)
        await chat.unban_member(user_id=user_id)
    except Exception as error:
        await message.reply_text(f"An error occurred: {str(error)}")
    else:
        await message.reply_text("User has been unbanned in the specified chat.")
