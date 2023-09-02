from pyrogram import Client, filters
from pyrogram.types import ChatPermissions
from info import *

# Updated extract_user function to extract user details
def get_user_details(message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    else:
        user = message.from_user

    user_id = user.id
    user_first_name = user.first_name

    return user_id, user_first_name

# Use @Client.on_message for both promote and demote commands
@Client.on_message(filters.command("promote_user") & filters.user(ADMINS))
async def promote_user(client, message):
    user_id, user_first_name = get_user_details(message)

    if not user_id:
        await message.reply_text("You don't seem to be referring to a user.")
        return

    try:
        user_member = await client.get_chat_member(message.chat.id, user_id)

        if user_member.status in ('administrator', 'creator'):
            await message.reply_text("The user is already an admin or creator.")
            return

        if user_id == client.me.id:
            await message.reply_text("I can't promote myself! Get an admin to do it for me.")
            return

        permissions = ChatPermissions(
            can_change_info=True,
            can_send_messages=True,
            can_send_media_messages=True,
            can_invite_users=True,
            can_send_polls=True,
            can_pin_messages=True
        )

        await client.promote_chat_member(message.chat.id, user_id, permissions)
        

        await message.reply_text(
            f"✨ {user_first_name} has been promoted to an admin! 🎉"
        )
    except Exception as error:
        await message.reply_text(str(error))

@Client.on_message(filters.command("demote_user") & filters.user(ADMINS))
async def demote_user(client, message):
    user_id, user_first_name = get_user_details(message)

    if not user_id:
        await message.reply_text("You don't seem to be referring to a user.")
        return

    try:
        await client.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=user_id,
            permissions=ChatPermissions(can_send_messages=True)
        )

        await message.reply_text(f"🔥 {user_first_name} has been demoted to a regular member!")
    except Exception as error:
        await message.reply_text(str(error))
