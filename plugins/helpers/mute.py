from pyrogram import Client, filters
from pyrogram.types import ChatPermissions
from info import *

# Helper function to extract user details and permissions
permissions = ChatPermissions(
    can_send_messages=True,
    can_change_info=True,
    can_post_messages=True,
    can_edit_messages=True,
    can_delete_messages=True,
    can_invite_users=True,
    can_restrict_members=True,
    can_pin_messages=True,
    can_promote_members=True
)

# Updated extract_user function to extract user details
def get_user_details(message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        user_id = user.id
        user_first_name = user.first_name
    else:
        user_id = message.from_user.id
        user_first_name = message.from_user.first_name
    return user_id, user_first_name

@Client.on_message(filters.command("promote_user") & filters.user(ADMINS))
async def promote_user(client, message):
    is_admin = message.from_user and message.from_user.id in ADMINS

    if not is_admin:
        await message.reply_text(
            "Admin privileges are required to promote users."
        )
        return

    user_id, user_first_name = get_user_details(message)
    try:
        await message.chat.promote_member(
            user_id=user_id,
            can_change_info=True,
            can_post_messages=True,
            can_edit_messages=True,
            can_delete_messages=True,
            can_invite_users=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_promote_members=True
        )
        await message.reply_text(
            f"✨ {user_first_name} has been promoted to an admin! 🎉"
        )
    except Exception as error:
        await message.reply_text(str(error))

@Client.on_message(filters.command("demote_user") & filters.user(ADMINS))
async def demote_user(client, message):
    is_admin = message.from_user and message.from_user.id in ADMINS

    if not is_admin:
        await message.reply_text(
            "Admin privileges are required to demote users."
        )
        return

    user_id, user_first_name = get_user_details(message)
    permissions = ChatPermissions(
        can_send_messages=True,
        can_change_info=True,
        can_invite_users=True,
    )
    try:
        await message.chat.restrict_member(
            user_id=user_id,
            permissions=permissions
        )
        await message.reply_text(
            f"🔥 {user_first_name} has been demoted to a regular member!"
        )
    except Exception as error:
        await message.reply_text(str(error))
        
