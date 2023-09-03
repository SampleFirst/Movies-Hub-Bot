from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant
from pyrogram.types import ChatPrivileges
from info import ADMINS

# Replace this with your actual group chat ID
Chatid = -1001887687488


# Define your command handler
@Client.on_message(filters.command("addadmin") & filters.private)
async def add_admin(client, message):
    chat_id = Chatid  # Use the predefined Chatid

    if message.from_user.id not in ADMINS:
        await message.reply("You must be an admin to use this command.")
        return

    if len(message.command) != 2:
        await message.reply("Usage: /addadmin <user_id>")
        return

    user_id = int(message.command[1])

    try:
        await client.promote_chat_member(
            chat_id,
            user_id,
            privileges=ChatPrivileges(
                can_manage_chat=True,
                can_delete_messages=True,
                can_manage_video_chats=True,
                can_restrict_members=True,
                can_promote_members=True,
                can_change_info=True,
                can_post_messages=True,
                can_edit_messages=True,
                can_invite_users=True,
                can_pin_messages=True,
                is_anonymous=True
            ),
        )
        await message.reply("User added as an admin with specified privileges.")
    except UserNotParticipant:
        await message.reply("The user must be a member of the chat to use this command.")
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")
