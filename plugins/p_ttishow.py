# Standard Library Imports
import asyncio
import math

# Third-Party Library Imports
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid
from pyrogram.errors import ChatAdminRequired

# Database Imports
from database.users_chats_db import db
from database.ia_filterdb import Media

# Local Imports
from utils import get_size, temp, get_settings
from Script import script

# Environment Variables
from info import(
    ADMINS, 
    LOG_CHANNEL, 
    SUPPORT_CHAT, 
    MELCOW_NEW_USERS, 
    MELCOW_IMG, 
    MELCOW_VID, 
    MAIN_CHANNEL, 
    S_GROUP
)

# Define a dictionary to keep track of the current page for each user
user_pages = {}


@Client.on_message(filters.new_chat_members & filters.group)
async def save_group(bot, message):
    p_b_check = [u.id for u in message.new_chat_members]
    if temp.ME in p_b_check:
        if not await db.get_chat(message.chat.id):
            total = await bot.get_chat_members_count(message.chat.id)
            p_b = message.from_user.mention if message.from_user else "Anonymous"
            await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, p_b))
            await db.add_chat(message.chat.id, message.chat.title)
        
        if message.chat.id in temp.BANNED_CHATS:
            # Inspired from a boat of a banana tree
            buttons = [
                [
                    InlineKeyboardButton('Support', url=f'https://t.me/{SUPPORT_CHAT}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            k = await message.reply(
                text='<b>CHAT NOT ALLOWED 🐞\n\nMy admins have restricted me from working here! If you want to know more about it, contact support.</b>',
                reply_markup=reply_markup,
            )

            try:
                await k.pin()
            except:
                pass
            await bot.leave_chat(message.chat.id)
            return
        
        buttons = [
            [
                InlineKeyboardButton('ℹ️ Help', url=f"https://t.me/{temp.U_NAME}?start=help"),
                InlineKeyboardButton('📢 Updates', url=(MAIN_CHANNEL))
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(
            text=f"<b>Thank you For Adding Me In {message.chat.title} ❣️\n\nIf you have any questions & doubts about using me, contact support.</b>",
            reply_markup=reply_markup)
    else:
        settings = await get_settings(message.chat.id)
        if settings["welcome"]:
            for u in message.new_chat_members:
                if (temp.MELCOW).get('welcome') is not None:
                    try:
                        await (temp.MELCOW['welcome']).delete()
                    except:
                        pass
                temp.MELCOW['welcome'] = await message.reply_video(
                    video=(MELCOW_VID),
                    caption=(script.MELCOW_ENG.format(u.mention, message.chat.title)),
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton('Support Group', url=S_GROUP),
                                InlineKeyboardButton('Updates Channel', url=MAIN_CHANNEL)
                            ]
                        ]
                    ),
                    parse_mode=enums.ParseMode.HTML
                )
                
        if settings["auto_delete"]:
            await asyncio.sleep(600)
            await (temp.MELCOW['welcome']).delete()


@Client.on_message(filters.command('leave') & filters.user(ADMINS))
async def leave_a_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        chat = chat
    try:
        buttons = [
            [
                InlineKeyboardButton('Support', url=f'https://t.me/{SUPPORT_CHAT}')
            ]
        ]
        reply_markup=InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat,
            text='<b>Hello Friends, \nMy admin has told me to leave from group so i go! If you wanna add me again contact my support group.</b>',
            reply_markup=reply_markup,
        )

        await bot.leave_chat(chat)
        await message.reply(f"left the chat `{chat}`")
    except Exception as e:
        await message.reply(f'Error - {e}')


@Client.on_message(filters.command('disable') & filters.user(ADMINS))
async def disable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    cha_t = await db.get_chat(int(chat_))
    if not cha_t:
        return await message.reply("Chat Not Found In DB")
    if cha_t['is_disabled']:
        return await message.reply(f"This chat is already disabled:\nReason-<code> {cha_t['reason']} </code>")
    await db.disable_chat(int(chat_), reason)
    temp.BANNED_CHATS.append(int(chat_))
    await message.reply('Chat Successfully Disabled')
    try:
        buttons = [
            [
                InlineKeyboardButton('Support', url=f'https://t.me/{SUPPORT_CHAT}')
            ]
        ]
        reply_markup=InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat_, 
            text=f'<b>Hello Friends, \nMy admin has told me to leave from group so i go! If you wanna add me again contact my support group.</b> \nReason : <code>{reason}</code>',
            reply_markup=reply_markup)
        await bot.leave_chat(chat_)
    except Exception as e:
        await message.reply(f"Error - {e}")


@Client.on_message(filters.command('enable') & filters.user(ADMINS))
async def re_enable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    sts = await db.get_chat(int(chat))
    if not sts:
        return await message.reply("Chat Not Found In DB !")
    if not sts.get('is_disabled'):
        return await message.reply('This chat is not yet disabled.')
    await db.re_enable_chat(int(chat_))
    temp.BANNED_CHATS.remove(int(chat_))
    await message.reply("Chat Successfully re-enabled")


@Client.on_message(filters.command('stats') & filters.incoming)
async def get_ststs(bot, message):
    pra = await message.reply('Fetching stats..')
    total_users = await db.total_users_count()
    total_chats = await db.total_chat_count()
    files = await Media.count_documents()
    size = await db.get_db_size()
    free = 536870912 - size
    size = get_size(size)
    free = get_size(free)
    await pra.edit(script.STATUS_TXT.format(files, total_users, total_chats, size, free))


@Client.on_message(filters.command('invite') & filters.user(ADMINS))
async def gen_invite(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    try:
        link = await bot.create_chat_invite_link(chat)
    except ChatAdminRequired:
        return await message.reply("Invite Link Generation Failed, Iam Not Having Sufficient Rights")
    except Exception as e:
        return await message.reply(f'Error {e}')
    await message.reply(f'Here is your Invite Link {link.invite_link}')


@Client.on_message(filters.command('all_invite') & filters.private & filters.user(ADMINS))
async def gen_invite_pm(client, message):
    user_id = message.from_user.id
    current_page = user_pages.get(user_id, 1)

    await message.reply_text("Fetching invite links for chats where I'm an ADMIN...")

    chat_links = []

    # Retrieve all chats using your method
    all_chats_cursor = await db.get_all_chats()
    all_chats = await all_chats_cursor.to_list(length=None)  # Convert cursor to a list

    num_links_per_page = 10
    num_pages = math.ceil(len(all_chats) / num_links_per_page)

    start_index = (current_page - 1) * num_links_per_page
    end_index = start_index + num_links_per_page

    buttons = []

    for chat in all_chats[start_index:end_index]:
        try:
            chat_id = chat.get('id')  # Retrieve chat ID
            chat_title = chat.get('title')  # Retrieve chat title

            # Double-check if the chat ID and title are valid
            if chat_id and chat_title:
                buttons.append([InlineKeyboardButton(chat_title, callback_data=f"get_link_{chat_id}")])
            else:
                chat_links.append(f"Invalid chat data.\n")

        except Exception as e:
            chat_links.append(f"Chat: {chat_title}\nError: {e}\n")

    keyboard = buttons

    if num_pages > 1:
        if current_page > 1:
            keyboard.append([InlineKeyboardButton("Previous Page", callback_data="prev_page")])

        if current_page < num_pages:
            keyboard.append([InlineKeyboardButton("Next Page", callback_data="next_page")])

    await message.reply_text(
        "Select a chat to get the invite link:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@Client.on_callback_query(filters.regex(r"^get_link_\d+"))
async def get_invite_link(client, callback_query):
    chat_id = int(callback_query.data.split("_")[2])
    try:
        link = await client.create_chat_invite_link(chat_id)
        await callback_query.answer(link.invite_link)
    except ChatAdminRequired:
        await callback_query.answer("I don't have sufficient rights.")
    except Exception as e:
        await callback_query.answer(f"Error: {e}")
        
        
@Client.on_message(filters.command('ban') & filters.user(ADMINS))
async def ban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a user id / username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("This is an invalid user, make sure ia have met him before.")
    except IndexError:
        return await message.reply("This might be a channel, make sure its a user.")
    except Exception as e:
        return await message.reply(f'Error - {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if jar['is_banned']:
            return await message.reply(f"{k.mention} is already banned\nReason: {jar['ban_reason']}")
        await db.ban_user(k.id, reason)
        temp.BANNED_USERS.append(k.id)
        await message.reply(f"Successfully banned {k.mention}")


@Client.on_message(filters.command('unban') & filters.user(ADMINS))
async def unban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a user id / username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("This is an invalid user, make sure ia have met him before.")
    except IndexError:
        return await message.reply("Thismight be a channel, make sure its a user.")
    except Exception as e:
        return await message.reply(f'Error - {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if not jar['is_banned']:
            return await message.reply(f"{k.mention} is not yet banned.")
        await db.remove_ban(k.id)
        temp.BANNED_USERS.remove(k.id)
        await message.reply(f"Successfully unbanned {k.mention}")


@Client.on_message(filters.command('users') & filters.user(ADMINS))
async def list_users(bot, message):
    pra = await message.reply('Getting List Of Users')
    users = await db.get_all_users()
    out = "Users Saved In DB Are:\n\n"
    async for user in users:
        out += f"<a href=tg://user?id={user['id']}>{user['name']}</a>"
        if user['ban_status']['is_banned']:
            out += '( Banned User )'
        out += '\n'
    try:
        await pra.edit_text(out)
    except MessageTooLong:
        with open('users.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('users.txt', caption="List Of Users")


@Client.on_message(filters.command('chats') & filters.user(ADMINS))
async def list_chats(bot, message):
    pra = await message.reply('Getting List Of chats')
    chats = await db.get_all_chats()
    out = "Chats Saved In DB Are:\n\n"
    async for chat in chats:
        out += f"**Title:** `{chat['title']}`\n**- ID:** `{chat['id']}`"
        if chat['chat_status']['is_disabled']:
            out += '( Disabled Chat )'
        out += '\n'
    try:
        await pra.edit_text(out)
    except MessageTooLong:
        with open('chats.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('chats.txt', caption="List Of Chats")
        
