import asyncio
import re
import math
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.ia_filterdb import get_search_results

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Function to handle the command and show results in buttons for all files
async def show_all_files_command(client, message):
    chat_id = message.chat.id
    max_results = 10  # Adjust this value as needed
    files, offset, total_results = await get_search_results(chat_id, '', max_results=max_results, offset=0, filter=True)

    if not files:
        await message.reply("No files found.")
        return

    pre = 'pmfilep' if PROTECT_CONTENT else 'pmfile'

    btn = [
        [
            InlineKeyboardButton(text=f"[{file.file_name}]", callback_data=f'{pre}#{file.file_id}')
        ] 
        for file in files
    ]

    if offset != "":
        key = f"{message.message_id}"
        temp.PM_BUTTONS[key] = ''
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [
                InlineKeyboardButton(text=f"📄 Page 1/{math.ceil(total_results / max_results)}", callback_data="pages"),
                InlineKeyboardButton(text="Next ➡️", callback_data=f"pmnext_{req}_{key}_{offset}")
            ]
        )
    else:
        btn.append(
            [
                InlineKeyboardButton(text=f"📄 Page 1/1", callback_data="pages")
            ]
        )

        caption = f"Here are all available files:"
        abc = await message.reply(caption, reply_markup=InlineKeyboardMarkup(btn))

        await asyncio.sleep(IMDB_DELET_TIME)
        await abc.delete()

# Add a command handler for /showallfiles command
@Client.on_message(filters.command(["showallfiles"]) & filters.private & filters.user(AUTH_USERS))
async def show_all_files(client, message):
    await show_all_files_command(client, message)

