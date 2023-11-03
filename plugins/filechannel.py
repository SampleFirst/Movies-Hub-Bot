import math
from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters
from database.ia_filterdb import Media, get_all_files
from info import ADMINS, MAX_BTTN

max_results = MAX_BTTN

@Client.on_message(filters.command("getallmedia") & filters.user(ADMINS))
async def send_all_media(client, message):
    try:
        files, offset, total_results = await get_all_files(max_results=max_results)

        btn = [
            [InlineKeyboardButton(text=f"{file.file_name}", callback_data=f'send#{file.file_id}')]
            for file in files
        ]

        btn.insert([
            InlineKeyboardButton("! Sᴇɴᴅ Aʟʟ Tᴏ PM !", callback_data=f"get_all")
        ])
        if offset:
            page_number = int(offset) // max_results
            btn.append([
                InlineKeyboardButton(text=f"📄 Page {page_number}/{math.ceil(total_results / max_results)}", callback_data="pages"),
                InlineKeyboardButton(text="Next", callback_data=f"pmnext_{offset}")
            ])
        else:
            btn.append([InlineKeyboardButton(text=f"📄 Page 1/1", callback_data="pages")])

        cap = f"Here are the {total_results} media files found in the database."

        abc = await message.reply_text(cap, quote=True, reply_markup=InlineKeyboardMarkup(btn))
    except Exception as e:
        # Handle any exceptions here
        print(f"An error occurred: {str(e)}")

@Client.on_callback_query(filters.regex(r'^pmnext_'))
async def next_page_button(client, query: CallbackQuery):
    try:
        offset = query.data.split("_")[1]
        files, new_offset, total_results = await get_all_files(max_results=max_results, offset=int(offset))
        page_number = int(offset) // max_results + 1

        btn = [
            [InlineKeyboardButton(text=f"{file.file_name}", callback_data=f'send#{file.file_id}')]
            for file in files
        ]
        btn.insert([
            InlineKeyboardButton("! Sᴇɴᴅ Aʟʟ Tᴏ PM !", callback_data=f"get_all")
        ])
        if new_offset:
            page_number = int(new_offset) // max_results + 1
            prev_offset = int(offset) - max_results  # Calculate the previous page offset
            if prev_offset >= 0:
                btn.append([
                    InlineKeyboardButton(text="Previous", callback_data=f"pmprev_{prev_offset}"),
                    InlineKeyboardButton(text=f"📄 Page {page_number}/{math.ceil(total_results / max_results)}", callback_data="pages"),
                    InlineKeyboardButton(text="Next", callback_data=f"pmnext_{new_offset}")
                ])
            else:
                btn.append([
                    InlineKeyboardButton(text=f"📄 Page {page_number}/{math.ceil(total_results / max_results)}", callback_data="pages"),
                    InlineKeyboardButton(text="Next", callback_data=f"pmnext_{new_offset}")
                ])
        else:
            btn.append([InlineKeyboardButton(text=f"📄 Page {page_number}/{math.ceil(total_results / max_results)}", callback_data="pages")]

        await query.edit_message_text(
            text=query.message.text.markdown,
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except Exception as e:
        # Handle any exceptions here
        print(f"An error occurred: {str(e)}")

@Client.on_callback_query(filters.regex(r'^pmprev_'))
async def prev_page_button(client, query: CallbackQuery):
    try:
        offset = query.data.split("_")[1]
        files, new_offset, total_results = await get_all_files(max_results=max_results, offset=int(offset))
        page_number = int(offset) // max_results + 1

        btn = [
            [InlineKeyboardButton(text=f"{file.file_name}", callback_data=f'send#{file.file_id}')]
            for file in files
        ]
        btn.insert([
            InlineKeyboardButton("! Sᴇɴᴅ Aʟʟ Tᴏ PM !", callback_data=f"get_all")
        ])
        if new_offset:
            page_number = int(new_offset) // max_results + 1
            prev_offset = int(offset) - max_results
            next_offset = int(offset) + max_results

            if prev_offset >= 0:
                btn.append([
                    InlineKeyboardButton(text="Previous", callback_data=f"pmprev_{prev_offset}"),
                    InlineKeyboardButton(text=f"📄 Page {page_number}/{math.ceil(total_results / max_results)}", callback_data="pages"),
                ])
            if next_offset < total_results:
                btn.append([
                    InlineKeyboardButton(text=f"📄 Page {page_number}/{math.ceil(total_results / max_results)}", callback_data="pages"),
                    InlineKeyboardButton(text="Next", callback_data=f"pmnext_{next_offset}")
                ])
                await query.edit_message_text(
                    text=query.message.text.markdown,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
        else:
            btn.append([InlineKeyboardButton(text=f"📄 Page {page_number}/{math.ceil(total_results / max_results)}", callback_data="pages")])

        await query.edit_message_text(
            text=query.message.text.markdown,
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except Exception as e:
        # Handle any exceptions here
        print(f"An error occurred: {str(e)}")

