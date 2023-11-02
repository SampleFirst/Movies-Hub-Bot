import math
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters
from database.ia_filterdb import Media, get_all_files
from info import ADMINS  # Make sure to define this constant in your info.py

@Client.on_message(filters.command("getallmedia") & filters.user(ADMINS))
async def send_all_media(client, message):
    files, offset, total_results = await get_all_files()
    
    btn = [
        [
            InlineKeyboardButton(text=f"{file.file_name}", callback_data=f'send#{file.file_id}')
        ] 
        for file in files 
    ]
    
    if offset != "":
        btn.append(
            [
                InlineKeyboardButton(text=f"📄 Page 1/{math.ceil(total_results / 6)}", callback_data="pages"),
                InlineKeyboardButton(text="Next ➡️", callback_data=f"pmnext_{offset}")
            ]
        )
    else:
        btn.append(
            [
                InlineKeyboardButton(text="📄 Page 1/1", callback_data="pages")
            ]
        )

    cap = f"Here are the {total_results} media files found in the database."
 
    abc = await message.reply_text(cap, quote=True, reply_markup=InlineKeyboardMarkup(btn))
