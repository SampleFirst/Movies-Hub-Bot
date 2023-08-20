# Standard Library Imports
import asyncio
import ast
import math
import random
import re
import logging
import datetime

from pytz import timezone

# Third-Party Library Imports
import pyrogram
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty

# Database Imports
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, make_inactive
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results, get_bad_files
from database.filters_mdb import del_all, find_filter, get_filters
from database.gfilters_mdb import find_gfilter, get_gfilters

# Local Imports
from Script import script
from utils import (
    get_size,
    is_subscribed,
    get_poster,
    search_gagala,
    temp,
    get_settings,
    save_group_settings,
    get_shortlink
)

# Environment Variables
from info import (
    ADMINS,
    AUTH_CHANNEL,
    FILE_CHANNEL,
    AUTH_USERS,
    CUSTOM_FILE_CAPTION,
    NOR_IMG,
    AUTH_GROUPS,
    P_TTI_SHOW_OFF,
    IMDB,
    SINGLE_BUTTON,
    SPELL_CHECK_REPLY,
    IMDB_TEMPLATE,
    SPELL_IMG,
    MSG_ALRT,
    FILE_FORWARD,
    MAIN_CHANNEL,
    LOG_CHANNEL_PM,
    PICS,
    SUPPORT_CHAT_ID
)

# Logging Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Global Variables
BUTTONS = {}
SPELL_CHECK = {}
FILTER_MODE = {}
back_stack = []


@Client.on_message(filters.command('autofilter') & filters.user(ADMINS))
async def fil_mod(client, message): 
      mode_on = ["yes", "on", "true"]
      mode_of = ["no", "off", "false"]

      try: 
         args = message.text.split(None, 1)[1].lower() 
      except: 
         return await message.reply("**𝙸𝙽𝙲𝙾𝙼𝙿𝙴𝚃𝙴𝙽𝚃 𝙲𝙾𝙼𝙼𝙰𝙳...**")
      
      m = await message.reply("**𝚂𝙴𝚃𝚃𝙸𝙽𝙶.../**")

      if args in mode_on:
          FILTER_MODE[str(message.chat.id)] = "True" 
          await m.edit("**𝙰𝚄𝚃𝙾𝙵𝙸𝙻𝚃𝙴𝚁 𝙴𝙽𝙰𝙱𝙻𝙴𝙳**")
      
      elif args in mode_of:
          FILTER_MODE[str(message.chat.id)] = "False"
          await m.edit("**𝙰𝚄𝚃𝙾𝙵𝙸𝙻𝚃𝙴𝚁 𝙳𝙸𝚂𝙰𝙱𝙻𝙴𝙳**")
      else:
          await m.edit("𝚄𝚂𝙴 :- /autofilter on 𝙾𝚁 /autofilter off")

@Client.on_message((filters.group) & filters.text & filters.incoming)
async def give_filter(client,message):
    await global_filters(client, message)
    group_id = message.chat.id
    name = message.text

    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            await message.reply_text(reply_text, disable_web_page_preview=True)
                        else:
                            button = eval(btn)
                            await message.reply_text(
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button)
                            )
                    elif btn == "[]":
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or ""
                        )
                    else:
                        button = eval(btn) 
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button)
                        )
                except Exception as e:
                    print(e)
                break 

    else:
        if FILTER_MODE.get(str(message.chat.id)) == "False":
            return
        else:
            await auto_filter(client, message)

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_text(bot, message):
    content = message.text
    user = message.from_user.first_name
    user_id = message.from_user.id

    # Set the timezone to India
    india_timezone = timezone('Asia/Kolkata')
    now = datetime.datetime.now(india_timezone)

    # Get the current time of day and date
    current_hour = now.hour
    time_suffix = "AM" if current_hour < 12 else "PM"
    formatted_time = now.strftime('%I:%M %p').lstrip('0')

    # Get the current date in Day-Month Name-Year format
    formatted_date = now.strftime('%d-%B %Y')

    if 5 <= current_hour < 12:
        greeting = "Good morning ☀️"
    elif 12 <= current_hour < 18:
        greeting = "Good afternoon 🌤️"
    elif 18 <= current_hour < 22:
        greeting = "Good evening 🌇"
    else:
        greeting = "Good night 🌙"

    if content.startswith("/") or content.startswith("#"):
        return  # ignore commands and hashtags
    if user_id in ADMINS:
        return  # ignore admins

    # Get the total users count
    total_users = await db.total_users_count()

    reply_text = f"<b>{greeting}, {user}!\n🎉 Thanks For Choosing Us\n\nJoin Our **𝙿𝚄𝙱𝙻𝙸𝙲 𝙶𝚁𝙾𝚄𝙿** For Sending Movie Names in Group Bot Reply Movies\n\nIf You Want Private Search Movies, Join Our **𝙿𝙼 𝚂𝙴𝙰𝚁𝙲𝙷** Bot to Send Movie Names. Bot Will Reply with Movies\n\nIf Any Bot Is Down, Check the Alternatives in **𝙼𝙾𝚁𝙴 𝙱𝙾𝚃𝚂** Official Channel</b>"

    # Create buttons for the reply message
    buttons = [
        [
            InlineKeyboardButton("𝙿𝚄𝙱𝙻𝙸𝙲 𝙶𝚁𝙾𝚄𝙿", url="https://t.me/iPapkornMoviesGroup"),
            InlineKeyboardButton("𝙿𝙼 𝚂𝙴𝙰𝚁𝙲𝙷", url="https://t.me/iPepkornBot?start")
        ],
        [
            InlineKeyboardButton("𝙼𝙾𝚁𝙴 𝙱𝙾𝚃𝚂", url="https://t.me/iPepkornBots/8")
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    # Set quote to True
    quote = True

    # Send the reply message with buttons
    await message.reply_text(
        text=reply_text,
        reply_markup=keyboard,
        quote=quote
    )

    # Send the log message to the specified channel with a button to send a message to the user
    log_buttons = [
        [
            InlineKeyboardButton("Send Message to User", callback_data=f"send_message:{user_id}")
        ]
    ]
    log_keyboard = InlineKeyboardMarkup(log_buttons)

    await bot.send_message(
        chat_id=LOG_CHANNEL_PM,
        text=f"<b>#PM_MSG\n\nUser: {user}\nID: {user_id}\n\nMessage: {content}\n\nDate: {formatted_date}\nTime: {formatted_time}\nTotal Users: {total_users}</b>",
        reply_markup=log_keyboard,
    )

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name),show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    settings = await get_settings(query.message.chat.id)
    if 'is_shortlink' in settings.keys():
        ENABLE_SHORTLINK = settings['is_shortlink']
    else:
        await save_group_settings(query.message.chat.id, 'is_shortlink', False)
        ENABLE_SHORTLINK = False
    if ENABLE_SHORTLINK == True:
        if settings['button']:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {file.file_name}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
    else:
        if settings['button']:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {file.file_name}", callback_data=f'files#{file.file_id}'
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}", callback_data=f'files#{file.file_id}'
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        callback_data=f'files_#{file.file_id}',
                    ),
                ]
                for file in files
        ]
    btn.insert(0, 
        [
            InlineKeyboardButton(f' ♀️ {search} ♀️ ', 'qinfo')
        ]
    )
    btn.insert(1, 
         [
             InlineKeyboardButton(f'ɪɴꜰᴏ', 'reqinfo'),
             InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
             InlineKeyboardButton(f'sᴇʀɪᴇs', 'sinfo'),
             InlineKeyboardButton(f'ᴛɪᴘs', 'tinfo')
         ]
    )

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"𝐏𝐀𝐆𝐄 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                                  callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"{math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
             InlineKeyboardButton("𝐍𝐄𝐗𝐓 ⌦", callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"𝐏𝐀𝐆𝐄 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("𝐍𝐄𝐗𝐓 ⌦", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()

# spellcheck error fixing
@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name),show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movie = movies[(int(movie_))]
    await query.answer(script.TOP_ALRT_MSG)
    k = await manual_filters(bot, query.message, text=movie)
    if k == False:
        files, offset, total_results = await get_search_results(movie, offset=0, filter=True)
        if files:
            k = (movie, files, offset, total_results)
            await auto_filter(bot, query, k)
        else:
            reqstr1 = query.from_user.id if query.from_user else 0
            reqstr = await bot.get_users(reqstr1)
            await bot.send_message(chat_id=LOG_CHANNEL_PM, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, movie)))
            k = await query.message.edit(script.MVE_NT_FND)
            await asyncio.sleep(10)
            await k.delete()


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    is_admin = query.from_user.id in ADMINS
    data = query.data
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make sure I'm present in your group!!", quote=True)
                    return await query.answer(MSG_ALRT)
            else:
                await query.message.edit_text(
                    "I'm not connected to any groups!\nCheck /connections or connect to any groups",
                    quote=True
                )
                return await query.answer(MSG_ALRT)

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer(MSG_ALRT)

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("You need to be Group Owner or an Auth User to do that!", show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer(script.ALRT_TXT.format(query.from_user.first_name),show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer(MSG_ALRT)
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Some error occurred!!', parse_mode=enums.ParseMode.MARKDOWN)
        return await query.answer(MSG_ALRT)
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return await query.answer(MSG_ALRT)
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "gfilteralert" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_gfilter('gfilters', keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        clicked = query.from_user.id
        
        try:
            typed = query.message.reply_to_message.from_user.id
        except:
            typed = clicked
        
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
            
        if f_caption is None:
            f_caption = f"{files.file_name}"
        
        try:
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                if clicked == typed:
                    await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                    return
                else:
                    await query.answer(f"Hᴇʏ {query.from_user.first_name}, Tʜɪs Is Nᴏᴛ Yᴏᴜʀ Mᴏᴠɪᴇ Rᴇǫᴜᴇsᴛ. Rᴇǫᴜᴇsᴛ Yᴏᴜʀ's !", show_alert=True)
            elif settings['botpm']:
                if clicked == typed:
                    await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                    return
                else:
                    await query.answer(f"Hᴇʏ {query.from_user.first_name}, Tʜɪs Is Nᴏᴛ Yᴏᴜʀ Mᴏᴠɪᴇ Rᴇǫᴜᴇsᴛ. Rᴇǫᴜᴇsᴛ Yᴏᴜʀ's !", show_alert=True)
            else:
                if clicked == typed:
                    file_send = await client.send_cached_media(
                        chat_id=FILE_CHANNEL,
                        file_id=file_id,
                        caption=script.CHANNEL_CAP.format(query.from_user.mention, title, query.message.chat.title),
                        protect_content=True if ident == "filep" else False,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton("⚠️ हिंदी", callback_data="hin"),
                                    InlineKeyboardButton("⚠️ தமிழ்", callback_data="tam"),
                                    InlineKeyboardButton("⚠️ తెలుగు", callback_data="tel")
                                ],
                                [
                                    InlineKeyboardButton("🔥 𝚄𝙿𝙳𝙰𝚃𝙴 𝙲𝙷𝙰𝙽𝙽𝙴𝙻 🔥", url=(MAIN_CHANNEL))
                                ], 
                            ]
                        )
                    )
                    Joel_tgx = await query.message.reply_text(
                        script.FILE_MSG.format(query.from_user.mention, title, size),
                        parse_mode=enums.ParseMode.HTML,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton('📥 𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽 𝖫𝗂𝗇𝗄 📥 ', url=file_send.link)
                                ], 
                                [
                                    InlineKeyboardButton("⚠️ 𝖢𝖺𝗇'𝗍 𝖠𝖼𝖼𝖾𝗌𝗌 ❓ 𝖢𝗅𝗂𝖼𝗄 𝖧𝖾𝗋𝖾 ⚠️", url=(FILE_FORWARD))
                                ]
                            ]
                        )
                    )
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await Joel_tgx.delete()
                        await file_send.delete()
                else:
                    return await query.answer(f"Hey {query.from_user.first_name}, this is not your movie request. Request yours!", show_alert=True)
        except UserIsBlocked:
            await query.answer('Unblock the bot!', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.answer("Join our backup channel, mahnn! 😒", show_alert=True)
            return
        ident, file_id = query.data.split("#")        
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exists.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        await query.answer()
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if ident == 'checksubp' else False
        )
    elif query.data == "predvd":
        files, next_offset, total = await get_bad_files('predvd', offset=0)
        if total > 0:
            confirm_btns = [
                [
                    InlineKeyboardButton("☑️ Confirm Deletion", callback_data="confirm_delete predvd"),
                    InlineKeyboardButton("❎Cancel", callback_data="cancel_deletefiles")
                ],
                [
                    InlineKeyboardButton("🏠 Home", callback_data="deletefiles")
                ]
            ]
            await query.message.edit_text(
                f"<b>✨ {total} PreDVD files detected. Are you sure you want to delete them?</b>",
                reply_markup=InlineKeyboardMarkup(confirm_btns)
            )
            # Save the current page to the back stack
            back_stack.append({
                'text': query.message.caption or query.message.text,
                'reply_markup': query.message.reply_markup
            })
        else:
            # Add buttons for going back and canceling
            btn = [
                [
                    InlineKeyboardButton("🔙 Back", callback_data="deletefiles"),
                    InlineKeyboardButton("❎ Cancel", callback_data="cancel_deletefiles")
                ]
            ]
            await query.message.edit_text(
                "<b>❎ No PreDVD files found for deletion.</b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )

    elif query.data == "camrip":
        files, next_offset, total = await get_bad_files('camrip', offset=0)
        if total > 0:
            confirm_btns = [
                [
                    InlineKeyboardButton("☑️ Confirm Deletion", callback_data="confirm_delete camrip"),
                    InlineKeyboardButton("❎ Cancel", callback_data="cancel_deletefiles")
                ],
                [
                    InlineKeyboardButton("🏠 Home", callback_data="deletefiles")
                ]
            ]
            await query.message.edit_text(
                f"<b>✨ {total} CamRip files detected. Are you sure you want to delete them?</b>",
                reply_markup=InlineKeyboardMarkup(confirm_btns)
            )
            # Save the current page to the back stack
            back_stack.append({
                'text': query.message.caption or query.message.text,
                'reply_markup': query.message.reply_markup
            })
        else:
            # Add buttons for going back and canceling
            btn = [
                [
                    InlineKeyboardButton("🔙 Back", callback_data="deletefiles"),
                    InlineKeyboardButton("❎ Cancel", callback_data="cancel_deletefiles")
                ]
            ]
            await query.message.edit_text(
                "<b>❎ No CamRip files found for deletion.</b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )

    elif query.data == "hdcam":
        files, next_offset, total = await get_bad_files('hdcam', offset=0)
        if total > 0:
            confirm_btns = [
                [
                    InlineKeyboardButton("☑️ Confirm Deletion", callback_data="confirm_delete hdcam"),
                    InlineKeyboardButton("❎ Cancel", callback_data="cancel_deletefiles")
                ],
                [
                    InlineKeyboardButton("🏠 Home", callback_data="deletefiles")
                ]
            ]
            await query.message.edit_text(
                f"<b>✨ {total} HDCam files detected. Are you sure you want to delete them?</b>",
                reply_markup=InlineKeyboardMarkup(confirm_btns)
            )
            # Save the current page to the back stack
            back_stack.append({
                'text': query.message.caption or query.message.text,
                'reply_markup': query.message.reply_markup
            })
        else:
            # Add buttons for going back and canceling
            btn = [
                [
                    InlineKeyboardButton("🔙 Back", callback_data="deletefiles"),
                    InlineKeyboardButton("❎ Cancel", callback_data="cancel_deletefiles")
                ]
            ]
            await query.message.edit_text(
                "<b>❎ No HDCam files found for deletion.</b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )

    elif query.data == "s-print":
        files, next_offset, total = await get_bad_files('s-print', offset=0)
        if total > 0:
            confirm_btns = [
                [
                    InlineKeyboardButton("☑️ Confirm Deletion", callback_data="confirm_delete s-print"),
                    InlineKeyboardButton("❎ Cancel", callback_data="cancel_deletefiles")
                ],
                [
                    InlineKeyboardButton("🏠 Home", callback_data="deletefiles")
                ]
            ]
            await query.message.edit_text(
                f"<b>✨ {total} S-Print files detected. Are you sure you want to delete them?</b>",
                reply_markup=InlineKeyboardMarkup(confirm_btns)
            )
            # Save the current page to the back stack
            back_stack.append({
                'text': query.message.caption or query.message.text,
                'reply_markup': query.message.reply_markup
            })
        else:
            # Add buttons for going back and canceling
            btn = [
                [
                    InlineKeyboardButton("🔙 Back", callback_data="deletefiles"),
                    InlineKeyboardButton("❎ Cancel", callback_data="cancel_deletefiles")
                ]
            ]
            await query.message.edit_text(
                "<b>❎ No S-Print files found for deletion.</b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )
    
    elif query.data == "hdtvrip":
        files, next_offset, total = await get_bad_files('hdtvrip', offset=0)
        if total > 0:
            confirm_btns = [
                [
                    InlineKeyboardButton("☑️ Confirm Deletion", callback_data="confirm_delete hdtvrip"),
                    InlineKeyboardButton("❎ Cancel", callback_data="cancel_deletefiles")
                ],
                [
                    InlineKeyboardButton("🏠 Home", callback_data="deletefiles")
                ]
            ]
            await query.message.edit_text(
                f"<b>✨ {total} HDTVrip files detected. Are you sure you want to delete them?</b>",
                reply_markup=InlineKeyboardMarkup(confirm_btns)
            )
            # Save the current page to the back stack
            back_stack.append({
                'text': query.message.caption or query.message.text,
                'reply_markup': query.message.reply_markup
            })
        else:
            # Add buttons for going back and canceling
            btn = [
                [
                    InlineKeyboardButton("🔙 Back", callback_data="deletefiles"),
                    InlineKeyboardButton("❎ Cancel", callback_data="cancel_deletefiles")
                ]
            ]
            await query.message.edit_text(
                "<b>❎ No HDTVrip files found for deletion.</b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )
   
    elif query.data.startswith("confirm_delete"):
        file_type = query.data.split()[1]
        files, next_offset, total = await get_bad_files(file_type, offset=0)
        deleted = 0
        for file in files:
            file_ids = file.file_id
            result = await Media.collection.delete_one({'_id': file_ids})
            if result.deleted_count:
                logger.info(f'{file_type} File Found! Successfully deleted from the database.')
            deleted += 1
        deleted = str(deleted)
        await query.message.edit_text(f"<b>Successfully deleted {deleted} {file_type.capitalize()} files.</b>")

        # Add buttons for canceling and going back
        btn = [
            [
                InlineKeyboardButton("❎ Cancel", callback_data="cancel_deletefiles"),
            ],
            [
                InlineKeyboardButton("🏠 Back", callback_data="deletefiles"),
            ]
        ]
        await query.message.edit_text(
            text=f"<b>Successfully deleted {deleted} {file_type.capitalize()} files.</b>",
            reply_markup=InlineKeyboardMarkup(btn)
        )
    elif query.data == "cancel_deletefiles":
        await query.message.reply_text("<b>☑️ File deletion canceled.</b>")

    elif query.data == "deletefiles":
        # Check if there are any pages in the back stack
        if back_stack:
            previous_page = back_stack.pop()
            await query.message.edit_text(
                previous_page['text'],
                reply_markup=previous_page['reply_markup']
            )
        else:
            # If no previous page, remove the back button and show the original command page
            btn = [
                [
                    InlineKeyboardButton("Delete PreDVDs", callback_data="predvd"),
                    InlineKeyboardButton("Delete CamRips", callback_data="camrip")
                ],
                [
                    InlineKeyboardButton("Delete HDCams", callback_data="hdcam"),
                    InlineKeyboardButton("Delete S-Prints", callback_data="s-print")
                ],
                [
                    InlineKeyboardButton("Delete HDTVRip", callback_data="hdtvrip"),
                    InlineKeyboardButton("Cancel", callback_data="cancel_deletefiles")
                ]
            ]
            await query.message.edit_text(
                "<b>✨ Select the type of files you want to delete!\n\n✨ This will delete 100 files from the database for the selected type.</b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )
        
    elif query.data == "deletefiletype":
        btn = [
            [
                InlineKeyboardButton("📥 Document", callback_data="delete_filetype_document"),
                InlineKeyboardButton("🎬 Video", callback_data="delete_filetype_video"),
            ],
            [
                InlineKeyboardButton("🎧 Audio", callback_data="delete_filetype_audio"),
                InlineKeyboardButton("❎ Cancel", callback_data="dft_cancel"),
            ]
       ]

        await query.message.edit_text(
            "<b>🗑 Select the type of files you want to delete!\n\n🗑 This will delete related files from the database.</b>",
            reply_markup=InlineKeyboardMarkup(btn),
        )

        
    elif query == "find_document":
        total_files = file_database.get("Document")
        if total_files is not None:
            await callback_query.message.edit_text(
                f"<b>Total files saved for Document: {total_files}</b>"
            )
        else:
            await callback_query.message.edit_text("Invalid file type selected!")

    elif query == "find_video":
        total_files = file_database.get("Video")
        if total_files is not None:
            await callback_query.message.edit_text(
                f"<b>Total files saved for Video: {total_files}</b>"
            )
        else:
            await callback_query.message.edit_text("Invalid file type selected!")

    elif query == "find_audio":
        total_files = file_database.get("Audio")
        if total_files is not None:
            await callback_query.message.edit_text(
                f"<b>Total files saved for Audio: {total_files}</b>"
            )
        else:
            await callback_query.message.edit_text("Invalid file type selected!")

    elif query == "find_image":
        total_files = file_database.get("Image")
        if total_files is not None:
            await callback_query.message.edit_text(
                f"<b>Total files saved for Image: {total_files}</b>"
            )
        else:
            await callback_query.message.edit_text("Invalid file type selected!")

    elif query == "find_zip":
        total_files = file_database.get("Zip")
        if total_files is not None:
            await callback_query.message.edit_text(
                f"<b>Total files saved for Zip: {total_files}</b>"
            )
        else:
            await callback_query.message.edit_text("Invalid file type selected!")
            
    

    elif query == "find_cancel":
        await callback_query.answer()
        await callback_query.message.edit_text("<b>Operation canceled.</b>")

    
    elif query.data == "pages":
        await query.answer()
    
    elif query.data == "reqinfo":
        await query.answer("ℹ️ Information ℹ️\n\nThis message will be automatically deleted after 10 minutes.\n\nIf you don't see the requested movie/series file, check the next page.\n\nPowered by iPepkornBots", show_alert=True)
    
    elif query.data == "minfo":
        await query.answer("⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯\nMovie Request Format\n⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯\n\nGo to Google ➠ Type movie name ➠ Copy correct name ➠ Paste in this group\n\nExample: Avatar: The Way of Water\n\n🚫 Don't use ➠ ':(!,./)\n\n@iPepkornBots", show_alert=True)
    
    elif query.data == "sinfo":
        await query.answer("⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯\nSeries Request Format\n⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯\n\nGo to Google ➠ Type series name ➠ Copy correct name ➠ Paste in this group\n\nExample: Money Heist S01E01\n\n🚫 Don't use ➠ ':(!,./)\n\n@iPepkornBots", show_alert=True)      
    
    elif query.data == "tinfo":
        await query.answer("▣ Tips ▣\n\n★ Type correct spelling (Google)\n\n★ If you don't get your file in the button, click the next button.\n\n★ Continue this method to get your file\n\nPowered by iPepkornBots", show_alert=True)

    elif query.data == "hin":
        await query.answer("कॉपीराइट के कारण फ़ाइल यहां से 10 मिनट में डिलीट हो जाएगी इसलिए यहां से कहीं और ले जाकर डाउनलोड करें!", show_alert=True)

    elif query.data == "tam":
        await query.answer("பதிப்புரிமை காரணமாக, கோப்பு இங்கிருந்து 10 நிமிடங்களில் அகற்றப்படும், எனவே மேலே சென்று பதிவிறக்கவும்!", show_alert=True)

    elif query.data == "tel":
        await query.answer("కాపీరైట్ కారణంగా, ఫైల్ ఇక్కడి నుండి 10 నిమిషాల్లో తొలగించబడుతుంది, కనుక దాన్ని ఎక్కడికైనా వెళ్లి డౌన్‌లోడ్ చేసుకోండి!", show_alert=True)
    
    elif query.data == "surprise":
        btn = [
            [
                InlineKeyboardButton('Surprise', callback_data='start')
            ]
        ]
        reply_markup=InlineKeyboardMarkup(btn)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.SUR_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "start":
        if is_admin:
            admin_buttons = [
                [
                    InlineKeyboardButton("➕️ 𝙰𝙳𝙳 𝙼𝙴 𝚃𝙾 𝚈𝙾𝚄𝚁 𝙶𝚁𝙾𝚄𝙿 ➕️", url=f"http://t.me/{temp.U_NAME}?startgroup=true")
                ],
                [
                    InlineKeyboardButton("📊 𝚂𝚃𝙰𝚃𝚄𝚂", callback_data="bot_status"),
                    InlineKeyboardButton("🔍 𝚂𝙴𝙰𝚁𝙲𝙷", switch_inline_query_current_chat='')
                ],
                [
                    InlineKeyboardButton("ℹ️ 𝙷𝙴𝙻𝙿", callback_data="help"),
                    InlineKeyboardButton("💫 𝙰𝙱𝙾𝚄𝚃", callback_data="about")
                ],
                [
                    InlineKeyboardButton('🔒 𝙰𝙳𝙼𝙸𝙽 𝚂𝙴𝚃𝚃𝙸𝙽𝙶𝚂 🔒', callback_data='admin_settings')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(admin_buttons)
            await client.edit_message_media(
                query.message.chat.id, 
                query.message.id, 
                InputMediaPhoto(random.choice(PICS))
            )
            await query.message.edit_text(
                text=script.ADMIN_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            await query.answer(MSG_ALRT)            
        else:
            users_buttons = [
                [
                    InlineKeyboardButton("➕️ 𝙰𝙳𝙳 𝙼𝙴 𝚃𝙾 𝚈𝙾𝚄𝚁 𝙶𝚁𝙾𝚄𝙿 ➕️", url=f"http://t.me/{temp.U_NAME}?startgroup=true")
                ],
                [
                    InlineKeyboardButton("🤖 𝙼𝙾𝚁𝙴 𝙱𝙾𝚃𝚂", callback_data="bots"),
                    InlineKeyboardButton("📢 𝚄𝙿𝙳𝙰𝚃𝙴𝚂", url="https://t.me/iPapkornUpdate")
                ],
                [
                    InlineKeyboardButton("ℹ️ 𝙷𝙴𝙻𝙿", callback_data="help"),
                    InlineKeyboardButton("💫 𝙰𝙱𝙾𝚄𝚃", callback_data="about")
                ],
                [
                    InlineKeyboardButton('🌟 𝙹𝙾𝙸𝙽 𝚆𝙸𝚃𝙷 𝚈𝙾𝚄𝚃𝚄𝙱𝙴 🌟', url=f"https://youtube.com/@InvisibleYTV")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(users_buttons)
            await client.edit_message_media(
                query.message.chat.id, 
                query.message.id, 
                InputMediaPhoto(random.choice(PICS))
            )
            await query.message.edit_text(
                text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            await query.answer(MSG_ALRT)
    elif query.data == "help":
        buttons = [
            [
                InlineKeyboardButton('Filters', callback_data='filters'),
                InlineKeyboardButton('File Store', callback_data='store_file')
            ],
            [
                InlineKeyboardButton('Connection', callback_data='coct'),
                InlineKeyboardButton('Extra Mods', callback_data='extra')
            ],
            [
                InlineKeyboardButton('Home', callback_data='start'),
                InlineKeyboardButton('Status', callback_data='stats')
            ]
        ]
            
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "about":
        buttons = [
            [
                InlineKeyboardButton('Status', callback_data='stats'),
                InlineKeyboardButton('Source', callback_data='source')
            ],
            [
                InlineKeyboardButton('Home', callback_data='start'),
                InlineKeyboardButton('Close', callback_data='close_data')
            ]
        ]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "source":
        buttons = [[
            InlineKeyboardButton('ʀᴇᴘᴏ', url='https://t.me/iPepkornBots'),
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SOURCE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "manuelfilter":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('ʙᴜᴛᴛᴏɴs', callback_data='button')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MANUELFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "button":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='manuelfilter')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.BUTTON_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "autofilter":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.AUTOFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "coct":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "extra":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('ᴀᴅᴍɪɴ', callback_data='admin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.EXTRAMOD_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "admin":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='extra')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADMIN_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "song":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SONG_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "video":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.VIDEO_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "tts":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.TTS_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "gtrans":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='aswins'),
            InlineKeyboardButton('𝙻𝙰𝙽𝙶 𝙲𝙾𝙳𝙴𝚂', url='https://cloud.google.com/translate/docs/languages')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.GTRANS_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "country":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='aswins'),
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CON_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "tele":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.TELE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "corona":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='aswin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CORONA_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "abook":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='aswin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOOK_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "deploy":
        buttons = [[
           InlineKeyboardButton('ʀᴇᴘᴏ', url='https://t.me/iPepkornBots'),
           InlineKeyboardButton('ᴏᴡɴᴇʀ', url='https://t.me/iPepkornBots')
        ], [
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='aswin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.DEPLOY_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "sticker":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='aswin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.STICKER_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "pings":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='aswin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.PINGS_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "json":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.JSON_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "urlshort":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='aswin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.URLSHORT_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "whois":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='aswin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.WHOIS_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "font":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='aswins')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.FONT_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "carb":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='aswins')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CARB_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "fun":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='aswin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.FUN_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "stats":
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='start'),
            InlineKeyboardButton('ʀᴇғʀᴇsʜ', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "rfrsh":
        await query.answer("Fatching MongoDb Database")
        buttons = [[
            InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='stats'),
            InlineKeyboardButton('ʀᴇғʀᴇsʜ', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif data.startswith("notify_user_not_avail"):
        _, reqstr_id, movie = data.split(":")
        # Send message to user
        try:
            btn = [
                [
                    InlineKeyboardButton(text="💌 𝙼𝙾𝚅𝙸𝙴 𝙶𝚁𝙾𝚄𝙿 💌", url="https://t.me/iPapkornMoviesGroup")
                ],
                [
                    InlineKeyboardButton(text="🐞 𝚁𝙴𝙿𝙾𝚁𝚃 𝙸𝚂𝚂𝚄𝙴𝚂 🐞", url="https://t.me/iPapkornSupportGroup")
                ]
            ]
            btn_pop = [
                [
                    InlineKeyboardButton(text="✖️ 𝙲𝙰𝙽𝙲𝙴𝙻 ✖️", callback_data="close_data")
                ]
            ]
            reply_markup_pop = InlineKeyboardMarkup(btn_pop)
            reply_markup = InlineKeyboardMarkup(btn)
            await client.send_message(int(reqstr_id), f"😒 oops! sona, Your requested content named `{movie}` is not available right now, we are really trying our best to serve you this content, can you please provide us some more details related to your query {movie}, \nSend details to Admin : <a href='https://telegram.me/{ADMIN_USRNM}'>**Send here...**</a>\n\n❤ Thank You for the contribution", reply_markup=reply_markup)
            await query.edit_message_text(text=f"- __**User notified successfully sweetie...✅**__\n\n⏳**Status** : Not Available 😒.\n🪪**UserID** : `{reqstr_id}`\n🎞**Content** : `{movie}`\n\n\n🦋",reply_markup=reply_markup_lzdv)
            # Delete callback query message
            await query.answer()
            await query.delete()
        except Exception as e:
            print(e)  # print the error message
            await query.answer("something went wrong", show_alert=True)
            return
    elif data.startswith("notify_user_alrupl"):
        _, reqstr_id, movie = data.split(":")
        # Send message to user
        try:
            btn = [
                [
                    InlineKeyboardButton(text=f"💌 𝙼𝙾𝚅𝙸𝙴 𝙶𝚁𝙾𝚄𝙿 💌", url=f"https://t.me/iPapkornMoviesGroup")
                ],
                [
                    InlineKeyboardButton(text=f"🐞 𝚁𝙴𝙿𝙾𝚁𝚃 𝙸𝚂𝚂𝚄𝙴𝚂 🐞", url=f"https://t.me/iPapkornSupportGroup")
                ]
            ]
            btn_pop = [
                [
                    InlineKeyboardButton(text=f"✖️ 𝙲𝙰𝙽𝙲𝙴𝙻 ✖️", callback_data="close_data")
                ]
            ]
            reply_markup_pop = InlineKeyboardMarkup(btn_pop)
            reply_markup = InlineKeyboardMarkup(btn)
            await client.send_message(int(reqstr_id), f"🛋 Hey sona, Your requested content named `{movie}` is already available in our database! You can easily get this movie by searching its correct name in our official group...\nSend details to Admin : \n\n❤ Thank You for the contribution", reply_markup=reply_markup)
            await query.edit_message_text(text=f"- __**User notified successfully sweetie...✅**__\n\n⏳**Status** : Already Uploaded ⚡.\n🪪**UserID** : `{reqstr_id}`\n🎞**Content** : `{movie}`\n\n\n🦋", reply_markup=reply_markup_lzdv)
            # Delete callback query message
            await query.answer()
            await query.delete()
        except:
            await query.answer("something went wrong", show_alert=True)
            return
    elif data.startswith("notify_userupl"):
        _, reqstr.id, movie = data.split(":")
        # Send message to user
        try:
            btn = [
                [
                    InlineKeyboardButton(text=f"💌 𝙼𝙾𝚅𝙸𝙴 𝙶𝚁𝙾𝚄𝙿 💌", url=f"https://t.me/iPapkornMoviesGroup")
                ],
                [
                    InlineKeyboardButton(text=f"🐞 𝚁𝙴𝙿𝙾𝚁𝚃 𝙸𝚂𝚂𝚄𝙴𝚂 🐞", url=f"https://t.me/iPapkornSupportGroup")
                ]
            ]
            btn_pop = [
                [
                    InlineKeyboardButton(text=f"✖️ 𝙲𝙰𝙽𝙲𝙴𝙻 ✖️", callback_data="close_data")
                ]
            ]
            reply_markup_pop = InlineKeyboardMarkup(btn_pop)
            reply_markup = InlineKeyboardMarkup(btn)
            await client.send_message(int(reqstr.id), f"✅ Hey sona, Your requested content named `{movie}` is now available in our database! You can easily get this movie by searching its correct name in our official group...\n\n❤ Thank You for the contribution", reply_markup=reply_markup)
            await query.edit_message_text(text=f"- __**User notified successfully sweetie...✅**__\n\n⏳**Status** : Upload done ✅.\n🪪**UserID** : `{reqstr.id}`\n🎞**Content** : `{movie}`\n\n\n🦋", reply_markup=reply_markup_lzdv)
            # Delete callback query message
            await query.answer()
            await query.delete()
        except:
            await query.answer("something went wrong", show_alert=True)
            return
    elif data.startswith("notify_user_req_rejected"):
        _, reqstr.id, movie = data.split(":")
        # Send message to user
        try:
            btn = [
                [
                    InlineKeyboardButton(text=f"💌 𝙼𝙾𝚅𝙸𝙴 𝙶𝚁𝙾𝚄𝙿 💌", url=f"https://t.me/iPapkornMoviesGroup")
                ],
                [
                    InlineKeyboardButton(text=f"🐞 𝚁𝙴𝙿𝙾𝚁𝚃 𝙸𝚂𝚂𝚄𝙴𝚂 🐞", url=f"https://t.me/iPapkornSupportGroup")
                ]
            ]
            btn_pop = [
                [
                    InlineKeyboardButton(text=f"✖️ 𝙲𝙰𝙽𝙲𝙴𝙻 ✖️", callback_data="close_data")
                ]
            ]
            reply_markup_pop = InlineKeyboardMarkup(btn_pop)
            reply_markup = InlineKeyboardMarkup(btn)
            await client.send_message(int(reqstr.id), f"🙇‍♀️ Sorry Darling! Your requested content named `{movie}` is rejected by our **ADMiN**, we are really very sorry for the inconvenience, we can't process your request at the moment...\n\n❤️‍🩹Keep your search environment friendly, sweetheart!", reply_markup=reply_markup)
            await query.edit_message_text(text=f"- __**User notified successfully sweetie...✅**__\n\n⏳**Status** : Request Rejected ❌.\n🪪**UserID** : `{reqstr.id}`\n🎞**Content** : `{movie}`\n\n\n🦋",reply_markup=reply_markup_lzdv)
            # Delete callback query message
            await query.answer()
            await query.delete()
        except:
            await query.answer("something went wrong", show_alert=True)
            return
    elif data.startswith("notify_user_spelling_error"):
        _, reqstr.id, movie = data.split(":")
        # Send message to user
        try:
            btn = [
                [
                    InlineKeyboardButton(text=f"💌 𝙼𝙾𝚅𝙸𝙴 𝙶𝚁𝙾𝚄𝙿 💌", url=f"https://t.me/iPapkornMoviesGroup")
                ],
                [
                    InlineKeyboardButton(text=f"🐞 𝚁𝙴𝙿𝙾𝚁𝚃 𝙸𝚂𝚂𝚄𝙴𝚂 🐞", url=f"https://t.me/iPapkornSupportGroup")
                ]
            ]
            btn_pop = [
                [
                    InlineKeyboardButton(text=f"✖️ 𝙲𝙰𝙽𝙲𝙴𝙻 ✖️", callback_data="close_data")
                ]
            ]
            reply_markup_pop = InlineKeyboardMarkup(btn_pop)
            reply_markup = InlineKeyboardMarkup(btn)
            await client.send_message(int(reqstr.id), f"🌍 Your spelling matters.\nThe requested content `{movie}` is available in our database, You were unable to get it because of your spelling mistake.🧐 Please make sure you've spelled correctly while searching content in group...\n\n❤Thank u for supporting us.", reply_markup=reply_markup)
            await query.edit_message_text(text=f"- __**User notified successfully sweetie...✅**__\n\n⏳**Status** : Spelling error 🖊.\n🪪**UserID** : `{reqstr.id}`\n🎞**Content** : `{movie}`\n\n\n🦋", reply_markup=reply_markup_lzdv)
            # Delete callback query message
            await query.answer()
            await query.delete()
        except:
            await query.answer("something went wrong", show_alert=True)
            return
            
    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("Your Active Connection Has Been Changed. Go To /settings.")
            return await query.answer(MSG_ALRT)

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)
        try:
            if settings['auto_delete']:
                settings = await get_settings(grp_id)
        except KeyError:
            await save_group_settings(grp_id, 'auto_delete', True)
            settings = await get_settings(grp_id)

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Filter Button',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Single' if settings["button"] else 'Double',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Redirect To', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Bot PM' if settings["botpm"] else 'Channel',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('File Secure',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["file_secure"] else '❌ No',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('IMDB', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["imdb"] else '❌ No',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Spell Check',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["spell_check"] else '❌ No',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Welcome', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["welcome"] else '❌ No',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Auto Delete',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10 Mins' if settings["auto_delete"] else 'OFF',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ShortLink',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ ON' if settings["is_shortlink"] else '❌ OFF',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                ]
                
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
            await query.answer(MSG_ALRT)

async def auto_filter(client, msg, spoll=False):
    reqstr1 = msg.from_user.id if msg.from_user else 0
    reqstr = await client.get_users(reqstr1)
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)
        if message.text.startswith("/"):
            return  # ignore commands
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if len(message.text) < 100:
            search = message.text
            files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
            if not files:
                if settings["spell_check"]:
                    return await advantage_spell_chok(client, msg)
                else:
                    await client.send_message(
                        chat_id=LOG_CHANNEL_PM,
                        text=(script.NORSLTS.format(reqstr.id, reqstr.mention, search)),
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(text="✅Upload In", callback_data=f"notify_userupl:{reqstr.id}:{requested_movie}")
                                ],
                                [
                                    InlineKeyboardButton(text="⚡Already In", callback_data=f"notify_user_alrupl:{reqstr.id}:{requested_movie}"),
                                    InlineKeyboardButton(text="🖊Spell Error", callback_data=f"notify_user_spelling_error:{reqstr.id}:{requested_movie}")
                                ],
                                [
                                    InlineKeyboardButton(text="😒Not Available", callback_data=f"notify_user_not_avail:{reqstr.id}:{requested_movie}"),
                                    InlineKeyboardButton(text="❌Reject Req", callback_data=f"notify_user_req_rejected:{reqstr.id}:{requested_movie}")
                                ],
                            ]
                        )
                    )
                    
                    l = await message.reply_text(
                        text=(script.REPLY_TEXT.format(reqstr.id, reqstr.mention, search)),
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton("📋 𝚄𝙿𝙳𝙰𝚃𝙴 📋", url=f"https://t.me/iPapkornUpdate"),
                                    InlineKeyboardButton("🤖 𝙼𝙾𝚁𝙴 𝙱𝙾𝚃𝚂 🤖", url=f"https://t.me/iPepkornBots/8")
                                ]
                            ]
                        )
                    )
                    await asyncio.sleep(30)
                    await l.delete()
                    return
        else:
            return
    else:
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
        settings = await get_settings(message.chat.id)
    if 'is_shortlink' in settings.keys():
        ENABLE_SHORTLINK = settings['is_shortlink']
    else:
        await save_group_settings(message.chat.id, 'is_shortlink', False)
        ENABLE_SHORTLINK = False
    pre = 'filep' if settings['file_secure'] else 'file'
    if ENABLE_SHORTLINK == True:
        if settings["button"]:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {file.file_name}", url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}",
                        url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
    else:
        if settings["button"]:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {file.file_name}", callback_data=f'{pre}#{file.file_id}'
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}",
                        callback_data=f'{pre}#{file.file_id}',
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        callback_data=f'{pre}#{file.file_id}',
                    ),
                ]
                for file in files
            ]
    btn.insert(0, 
        [
            InlineKeyboardButton(f' ♀️ {search} ♀️ ', 'qinfo')
        ]
    )
    btn.insert(1, 
         [
             InlineKeyboardButton(f'ɪɴꜰᴏ', 'reqinfo'),
             InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
             InlineKeyboardButton(f'sᴇʀɪᴇs', 'sinfo'),
             InlineKeyboardButton(f'ᴛɪᴘs', 'tinfo')
         ]
    )

    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"𝐏𝐀𝐆𝐄 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
             InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ⌦", callback_data=f"next_{req}_{key}_{offset}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="𝐍𝐎 𝐌𝐎𝐑𝐄 𝐏𝐀𝐆𝐄𝐒 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄", callback_data="pages")]
        )
    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
    TEMPLATE = settings['template']
    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
    else:
        cap = f"<b><i>𝙃𝙚𝙧𝙚 𝙞𝙨 𝙬𝙝𝙖𝙩 𝙞𝙨 𝙛𝙤𝙪𝙣𝙙 𝙮𝙤𝙪𝙧 𝙦𝙪𝙚𝙧𝙮:\n {search}\n👤𝙍𝙚𝙦𝙪𝙚𝙨𝙩𝙚𝙙 𝘽𝙮 : {message.from_user.mention}\n👥𝙂𝙧𝙤𝙪𝙥 : {message.chat.title}</i></b>"
    if imdb and imdb.get('poster'):
        try:
            if message.chat.id == SUPPORT_CHAT_ID:
                await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, {str(total_results)} ʀᴇsᴜʟᴛs ᴀʀᴇ ғᴏᴜɴᴅ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {search}. Kɪɴᴅʟʏ ᴜsᴇ ɪɴʟɪɴᴇ sᴇᴀʀᴄʜ ᴏʀ ᴍᴀᴋᴇ ᴀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴀᴅᴅ ᴍᴇ ᴀs ᴀᴅᴍɪɴ ᴛᴏ ɢᴇᴛ ᴍᴏᴠɪᴇ ғɪʟᴇs. Tʜɪs ɪs ᴀ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ғɪʟᴇs ғʀᴏᴍ ʜᴇʀᴇ...</b>")
            else:
                hehe = await message.reply_photo(photo=imdb.get('poster'), caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))
                try:
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await hehe.delete()
                        await message.delete()
                except KeyError:
                    grpid = await active_connection(str(message.from_user.id))
                    await save_group_settings(grpid, 'auto_delete', True)
                    settings = await get_settings(message.chat.id)
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await hehe.delete()
                        await message.delete()
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            if message.chat.id == SUPPORT_CHAT_ID:
                await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, {str(total_results)} ʀᴇsᴜʟᴛs ᴀʀᴇ ғᴏᴜɴᴅ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {search}. Kɪɴᴅʟʏ ᴜsᴇ ɪɴʟɪɴᴇ sᴇᴀʀᴄʜ ᴏʀ ᴍᴀᴋᴇ ᴀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴀᴅᴅ ᴍᴇ ᴀs ᴀᴅᴍɪɴ ᴛᴏ ɢᴇᴛ ᴍᴏᴠɪᴇ ғɪʟᴇs. Tʜɪs ɪs ᴀ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ғɪʟᴇs ғʀᴏᴍ ʜᴇʀᴇ...</b>")
            else:
                pic = imdb.get('poster')
                poster = pic.replace('.jpg', "._V1_UX360.jpg")
                hmm = await message.reply_photo(photo=poster, caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))
                try:
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await hmm.delete()
                        await message.delete()
                except KeyError:
                    grpid = await active_connection(str(message.from_user.id))
                    await save_group_settings(grpid, 'auto_delete', True)
                    settings = await get_settings(message.chat.id)
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await hmm.delete()
                        await message.delete()
        except Exception as e:
            if message.chat.id == SUPPORT_CHAT_ID:
                await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, {str(total_results)} ʀᴇsᴜʟᴛs ᴀʀᴇ ғᴏᴜɴᴅ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {search}. Kɪɴᴅʟʏ ᴜsᴇ ɪɴʟɪɴᴇ sᴇᴀʀᴄʜ ᴏʀ ᴍᴀᴋᴇ ᴀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴀᴅᴅ ᴍᴇ ᴀs ᴀᴅᴍɪɴ ᴛᴏ ɢᴇᴛ ᴍᴏᴠɪᴇ ғɪʟᴇs. Tʜɪs ɪs ᴀ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ғɪʟᴇs ғʀᴏᴍ ʜᴇʀᴇ...</b>")
            else:
                logger.exception(e)
                fek = await message.reply_photo(photo=NOR_IMG, caption=cap, reply_markup=InlineKeyboardMarkup(btn))
                try:
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await fek.delete()
                        await message.delete()
                except KeyError:
                    grpid = await active_connection(str(message.from_user.id))
                    await save_group_settings(grpid, 'auto_delete', True)
                    settings = await get_settings(message.chat.id)
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await fek.delete()
                        await message.delete()
    else:
        if message.chat.id == SUPPORT_CHAT_ID:
            await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, {str(total_results)} ʀᴇsᴜʟᴛs ᴀʀᴇ ғᴏᴜɴᴅ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {search}. Kɪɴᴅʟʏ ᴜsᴇ ɪɴʟɪɴᴇ sᴇᴀʀᴄʜ ᴏʀ ᴍᴀᴋᴇ ᴀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴀᴅᴅ ᴍᴇ ᴀs ᴀᴅᴍɪɴ ᴛᴏ ɢᴇᴛ ᴍᴏᴠɪᴇ ғɪʟᴇs. Tʜɪs ɪs ᴀ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ғɪʟᴇs ғʀᴏᴍ ʜᴇʀᴇ...</b>")
        else:
            fuk = await message.reply_photo(photo=NOR_IMG, caption=cap, reply_markup=InlineKeyboardMarkup(btn))
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(600)
                    await fuk.delete()
                    await message.delete()
            except KeyError:
                grpid = await active_connection(str(message.from_user.id))
                await save_group_settings(grpid, 'auto_delete', True)
                settings = await get_settings(message.chat.id)
                if settings['auto_delete']:
                    await asyncio.sleep(600)
                    await fuk.delete()
                    await message.delete()
    
    if spoll:
        await msg.message.delete()


async def advantage_spell_chok(client, msg):
    mv_id = msg.id
    mv_rqst = msg.text
    reqstr1 = msg.from_user.id if msg.from_user else 0
    reqstr = await client.get_users(reqstr1)
    settings = await get_settings(msg.chat.id)
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE)  # plis contribute some common words
    RQST = query.strip()
    query = query.strip() + " movie"
    try:
        movies = await get_poster(mv_rqst, bulk=True)
    except Exception as e:
        logger.exception(e)
        await client.send_message(chat_id=LOG_CHANNEL_PM, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, mv_rqst)))
        k = await msg.reply(script.I_CUDNT.format(reqstr.mention))
        await asyncio.sleep(8)
        await k.delete()
        return
    movielist = []
    if not movies:
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [[
                   InlineKeyboardButton("Gᴏᴏɢʟᴇ", url=f"https://www.google.com/search?q={reqst_gle}")
        ]]
        await client.send_message(chat_id=LOG_CHANNEL_PM, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, mv_rqst)))
        k = await msg.reply_photo(
            photo=SPELL_IMG, 
            caption=script.I_CUDNT.format(mv_rqst),
            reply_markup=InlineKeyboardMarkup(button)
        )
        await asyncio.sleep(30)
        await k.delete()
        return
    movielist += [movie.get('title') for movie in movies]
    movielist += [f"{movie.get('title')} {movie.get('year')}" for movie in movies]
    SPELL_CHECK[mv_id] = movielist
    btn = [
        [
            InlineKeyboardButton(
                text=movie_name.strip(),
                callback_data=f"spol#{reqstr1}#{k}",
            )
        ]
        for k, movie_name in enumerate(movielist)
    ]
    btn.append([InlineKeyboardButton(text="Close", callback_data=f'spol#{reqstr1}#close_spellcheck')])
    spell_check_del = await msg.reply_photo(
        photo=(SPELL_IMG),
        caption=(script.CUDNT_FND.format(reqstr.mention)),
        reply_markup=InlineKeyboardMarkup(btn)
        )

    try:
        if settings['auto_delete']:
            await asyncio.sleep(600)
            await spell_check_del.delete()
    except KeyError:
            grpid = await active_connection(str(message.from_user.id))
            await save_group_settings(grpid, 'auto_delete', True)
            settings = await get_settings(message.chat.id)
            if settings['auto_delete']:
                await asyncio.sleep(600)
                await spell_check_del.delete()

async def manual_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            elsa = await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                protect_content=True if settings["file_secure"] else False,
                                reply_to_message_id=reply_id
                            )
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                            try:
                                if settings['auto_delete']:
                                    await asyncio.sleep(600)
                                    await elsa.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_delete', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_delete']:
                                    await asyncio.sleep(600)
                                    await elsa.delete()

                        else:
                            button = eval(btn)
                            hmm = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                protect_content=True if settings["file_secure"] else False,
                                reply_to_message_id=reply_id
                            )
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                            try:
                                if settings['auto_delete']:
                                    await asyncio.sleep(600)
                                    await hmm.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_delete', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_delete']:
                                    await asyncio.sleep(600)
                                    await hmm.delete()

                    elif btn == "[]":
                        oto = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            protect_content=True if settings["file_secure"] else False,
                            reply_to_message_id=reply_id
                        )
                        try:
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_ffilter', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                        try:
                            if settings['auto_delete']:
                                await asyncio.sleep(600)
                                await oto.delete()
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_delete', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_delete']:
                                await asyncio.sleep(600)
                                await oto.delete()

                    else:
                        button = eval(btn)
                        dlt = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                        try:
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_ffilter', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                        try:
                            if settings['auto_delete']:
                                await asyncio.sleep(600)
                                await dlt.delete()
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_delete', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_delete']:
                                await asyncio.sleep(600)
                                await dlt.delete()

                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False

async def global_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_gfilters('gfilters')
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_gfilter('gfilters', keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            joelkb = await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                reply_to_message_id=reply_id
                            )
                            
                        else:
                            button = eval(btn)
                            hmm = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )

                    elif btn == "[]":
                        oto = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )

                    else:
                        button = eval(btn)
                        dlt = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )                       

                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
