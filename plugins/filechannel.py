import math
from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters
from database.ia_filterdb import Media, get_all_files
from info import ADMINS

@Client.on_callback_query(filters.regex(r"^pmnext"))
async def pm_next_page(client, query):
    try:
        files, offset, total_results = await get_all_files()
        try:
            offset = int(offset)
        except ValueError:
            offset = 0

        if not files:
            return

        btn = [
            [
                InlineKeyboardButton(text=f"{file.file_name}", callback_data=f'send#{file.file_id}')
            ]
            for file in files
        ]

        if 0 < offset <= 10:
            off_set = 0
        elif offset == 0:
            off_set = None
        else:
            off_set = offset - 10

        if offset == 0:
            btn.append(
                [
                    InlineKeyboardButton("Back", callback_data=f"pmnext_{off_set}"),
                    InlineKeyboardButton(f"📃 Pages {math.ceil(int(offset) / 10) + 1} / {math.ceil(total_results / 10)}", callback_data="pages")
                ]
            )
        elif off_set is None:
            btn.append(
                [
                    InlineKeyboardButton(f"📃 Pages {math.ceil(int(offset) / 10) + 1} / {math.ceil(total_results / 10)}", callback_data="pages"),
                    InlineKeyboardButton("Next ", callback_data=f"pmnext_{offset + 10}")
                ]
            )
        else:
            btn.append(
                [
                    InlineKeyboardButton("Back", callback_data=f"pmnext_{off_set}"),
                    InlineKeyboardButton(f"📃 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total_results / 10)}", callback_data="pages"),
                    InlineKeyboardButton("Next", callback_data=f"pmnext_{offset + 10}")
                ]
            )

        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
        await query.answer()
    except Exception as e:
        # Handle any exceptions here
        print(f"An error occurred: {str(e)}")

@Client.on_message(filters.command("getallmedia") & filters.user(ADMINS))
async def send_all_media(client, message):
    try:
        files, offset, total_results = await get_all_files()

        btn = [
            [
                InlineKeyboardButton(text=f"{file.file_name}", callback_data=f'send#{file.file_id}')
            ]
            for file in files
        ]

        if offset:
            btn.append(
                [
                    InlineKeyboardButton(text=f"📄 Page 1/{math.ceil(total_results / 5)}", callback_data="pages"),
                    InlineKeyboardButton(text="Next", callback_data=f"pmnext_{offset}")
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
    except Exception as e:
        # Handle any exceptions here
        print(f"An error occurred: {str(e)}")
