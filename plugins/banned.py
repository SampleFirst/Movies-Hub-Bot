import asyncio
from pyrogram import Client, filters
from utils import temp
from pyrogram.types import Message
from database.users_chats_db import db
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import ADMINS, SUPPORT_CHAT, LOG_CHANNEL

# Initialize user violation counters
user_violations = {}


async def banned_users(_, client, message: Message):
    return (
        message.from_user is not None or not message.sender_chat
    ) and message.from_user.id in temp.BANNED_USERS

banned_user = filters.create(banned_users)

async def disabled_chat(_, client, message: Message):
    return message.chat.id in temp.BANNED_CHATS

disabled_group=filters.create(disabled_chat)


@Client.on_message(filters.private & banned_user & filters.incoming)
async def ban_reply(bot, message):
    ban = await db.get_ban_status(message.from_user.id)
    await message.reply(f'Sorry Dude, You are Banned to use Me. \nBan Reason: {ban["ban_reason"]}')

@Client.on_message(filters.group & disabled_group & filters.incoming)
async def grp_bd(bot, message):
    buttons = [[
        InlineKeyboardButton('Support', url=f'https://t.me/{SUPPORT_CHAT}')
    ]]
    reply_markup=InlineKeyboardMarkup(buttons)
    vazha = await db.get_chat(message.chat.id)
    k = await message.reply(
        text=f"CHAT NOT ALLOWED 🐞\n\nMy admins has restricted me from working here ! If you want to know more about it contact support..\nReason : <code>{vazha['reason']}</code>.",
        reply_markup=reply_markup)
    try:
        await k.pin()
    except:
        pass
    await bot.leave_chat(message.chat.id)




@Client.on_message(filters.text & filters.group)
async def delete_and_warn(client, message: Message):
    user_id = message.from_user.id
    message_text = message.text.lower()

    # Check if the user is an admin
    is_admin = user_id in ADMINS

    if is_admin:
        return

    # Check for links
    if "http://" in message_text or "https://" in message_text:
        await handle_violation(user_id, message, "link")
    else:
        # Check for keywords related to joining
        keywords = ["@" "join", "join channel", "channel"]
        for keyword in keywords:
            if keyword in message_text:
                await handle_violation(user_id, message, "keyword")
                break  # Exit loop after first keyword match

        # Check for usernames starting with "@"
        if message.entities:
            for entity in message.entities:
                if entity.type == "mention" and message_text[entity.offset] == "@":
                    await handle_violation(user_id, message, "username")
                    break

async def handle_violation(user_id, message, violation_type):
    user_violations[user_id] = user_violations.get(user_id, 0) + 1
    violation_count = user_violations[user_id]
    first_name = message.from_user.first_name

    if violation_type == "link":
        await warn_user(user_id, violation_count, first_name, "sending links")
    elif violation_type == "keyword":
        await warn_user(user_id, violation_count, first_name, "using keywords related to joining")
    elif violation_type == "username":
        await warn_user(user_id, violation_count, first_name, "sending usernames starting with '@'")

async def warn_user(user_id, count, first_name, violation_type):
    if count == 1:
        warning_msg = f"Hello {first_name}, sending {violation_type} is not allowed in this group. This is your first warning."
    elif count == 2:
        warning_msg = f"Hey {first_name}, you have been warned before for {violation_type}. This is your final warning. One more violation and you will be banned."
    elif count >= 3:
        await ban_user(user_id, first_name)

    await send_warning(user_id, warning_msg)

async def send_warning(user_id, warning_msg):
    await app.send_message(LOG_CHANNEL, f"User {user_id} received a warning: {warning_msg}")
    warning = await app.send_message(user_id, warning_msg)
    await asyncio.sleep(120)
    await warning.delete()

async def ban_user(user_id, first_name):
    try:
        await app.kick_chat_member(chat_id=message.chat.id, user_id=user_id)
    except Exception as error:
        await app.send_message(LOG_CHANNEL, f"Error banning user {user_id}: {str(error)}")
    else:
        ban_msg = f"Sorry {first_name}, you have been banned for repeated violations."
        await app.send_message(LOG_CHANNEL, f"User {user_id} was banned for repeated violations.")
        ban_warning = await app.send_message(user_id, ban_msg)
        await asyncio.sleep(120)
        await ban_warning.delete()

