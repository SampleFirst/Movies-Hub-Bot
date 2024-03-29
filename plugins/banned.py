import asyncio
from pyrogram import Client, filters
from utils import temp
from pyrogram.types import Message
from database.users_chats_db import db
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import ADMINS, SUPPORT_CHAT, LOG_CHANNEL

# A dictionary to keep track of users and their link counts
user_link_count = {}


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
async def delete_links_and_warn(client, message: Message):
    user_id = message.from_user.id

    # Check if the user is an admin
    is_admin = message.from_user and message.from_user.id in ADMINS

    if is_admin:
        return

    # Check if the message contains a link
    if "http://" in message.text or "https://" in message.text:
        # Increment link count for the user
        user_link_count[user_id] = user_link_count.get(user_id, 0) + 1

        # Delete the link message
        await message.delete()

        # Warn the user for sending a link
        if user_link_count[user_id] == 1:
            warning_msg = f"Sending links is not allowed in this group, {message.from_user.first_name}. This is your first warning."
            warning = await message.reply_text(warning_msg)
            await client.send_message(LOG_CHANNEL, f"User {user_id} received a first warning for sending a link.")
            await asyncio.sleep(120)
            await warning.delete()
            await message.delete()
        elif user_link_count[user_id] == 2:
            warning_msg = f"You have been warned before for sending links, {message.from_user.first_name}. This is your final warning. One more link and you will be banned."
            warning = await message.reply_text(warning_msg)
            await client.send_message(LOG_CHANNEL, f"User {user_id} received a final warning for sending a link.")
            await asyncio.sleep(120)
            await warning.delete()
            await message.delete()
        elif user_link_count[user_id] >= 3:
            try:
                await message.chat.ban_member(user_id=user_id)
            except Exception as error:
                await client.send_message(LOG_CHANNEL, f"Error banning user {user_id}: {str(error)}")
            else:
                ban_msg = f"You have been banned for sending links after multiple warnings, {message.from_user.first_name}."
                ban_warning = await message.reply_text(ban_msg)
                await client.send_message(LOG_CHANNEL, f"User {user_id} was banned for sending links after multiple warnings.")
                await asyncio.sleep(120)
                await ban_warning.delete()
                await message.delete()

        # Reset link count after a while (e.g., a day)
        await asyncio.sleep(24 * 60 * 60)  # Sleep for a day
        if user_id in user_link_count:
            del user_link_count[user_id]
            
