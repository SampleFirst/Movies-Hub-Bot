from pyrogram import Client, filters
from pyrogram.types import ChatPermissions
from plugins.helper_functions.admin_check import admin_check
from plugins.helper_functions.extract_user import extract_user                               
from plugins.helper_functions.string_handling import extract_time

@Client.on_message(filters.command("mute"))
async def mute_user(_, message):
    is_admin = await admin_check(message)
    if not is_admin:
        return
    user_id, user_first_name = extract_user(message)
    try:
        await message.chat.restrict_member(
            user_id=user_id,
            permissions=ChatPermissions(
            )
        )
    except Exception as error:
        await message.reply_text(
            str(error)
        )
    else:
        if str(user_id).lower().startswith("@"):
            await message.reply_text(
                "👍🏻 "
                f"{user_first_name}"
                " Lavender's mouth is shut! 🤐"
            )
        else:
            await message.reply_text(
                "👍🏻 "
                f"<a href='tg://user?id={user_id}'>"
                "Of lavender"
                "</a>"
                " The mouth is closed! 🤐"
            )


@Client.on_message(filters.command("tmute"))
async def temp_mute_user(_, message):
    is_admin = await admin_check(message)
    if not is_admin:
        return

    if not len(message.command) > 1:
        return

    user_id, user_first_name = extract_user(message)

    until_date_val = extract_time(message.command[1])
    if until_date_val is None:
        await message.reply_text(
            (
                "Invalid time type specified. "
                "Expected m, h, or d, Got it: {}"
            ).format(
                message.command[1][-1]
            )
        )
        return

    try:
        await message.chat.restrict_member(
            user_id=user_id,
            permissions=ChatPermissions(
            ),
            until_date=until_date_val
        )
    except Exception as error:
        await message.reply_text(
            str(error)
        )
    else:
        if str(user_id).lower().startswith("@"):
            await message.reply_text(
                "Be quiet for a while! 😠"
                f"{user_first_name}"
                f" muted for {message.command[1]}!"
            )
        else:
            await message.reply_text(
                "Be quiet for a while! 😠"
                f"<a href='tg://user?id={user_id}'>"
                "Of lavender"
                "</a>"
                " Mouth "
                f" muted for {message.command[1]}!"
            )
            
@Client.on_message(filters.command("promote_user"))
async def promote_user(_, message):
    is_admin = await admin_check(message)
    if not is_admin:
        await message.reply_text(
            "Attention: Admin Privileges Required\n\n"
            "Dear member,\n\n"
            "However, to access this, we kindly request that you ensure you have admin privileges within our group.",
            quote=True  # Add quote=True here
        )
        return

    user_id, user_first_name = extract_user(message)
    ChatPermissions = dict(
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
    try:
        await message.chat.promote_member(
            user_id=user_id,
            permissions=ChatPermissions
        )
    except Exception as error:
        await message.reply_text(str(error), quote=True)  # Add quote=True here
    else:
        await message.reply_text(
            f"✨ {user_first_name} has been promoted to an admin! 🎉",
            quote=True  # Add quote=True here
        )

@Client.on_message(filters.command("demote_user"))
async def demote_user(_, message):
    is_admin = await admin_check(message)
    if not is_admin:
        await message.reply_text(
            "Attention: Admin Privileges Required\n\n"
            "Dear member,\n\n"
            "To access this, we kindly request that you ensure you have admin privileges within our group.",
            quote=True  # Add quote=True here
        )
        return

    user_id, user_first_name = extract_user(message)
    ChatPermissions = dict(
        can_send_messages=True,
        can_change_info=False,
        can_post_messages=False,
        can_edit_messages=False,
        can_delete_messages=False,
        can_invite_users=False,
        can_restrict_members=False,
        can_pin_messages=False,
        can_promote_members=False
    )
    try:
        await message.chat.restrict_member(
            user_id=user_id,
            permissions=ChatPermissions
        )
    except Exception as error:
        await message.reply_text(str(error), quote=True)  # Add quote=True here
    else:
        await message.reply_text(
            f"🔥 {user_first_name} has been demoted to a regular member!",
            quote=True  # Add quote=True here
        )
