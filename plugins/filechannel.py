import asyncio
import math
import logging
from pyrogram.errors import MessageNotModified
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, PeerIdInvalid
from pyrogram import Client, filters
from database.ia_filterdb import Media, get_all_files, get_file_details
from info import ADMINS, MAX_BTTN, FILE_DB_CHANNEL
from utils import get_size

max_results = MAX_BTTN
MAX_BTN = 10
BATCH_SIZE = 10 # Number of media files to send in each batch
SEND_INTERVAL = 10  # Time interval (in seconds) between batches

# Logging Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@Client.on_message(filters.command("getallmedia") & filters.user(ADMINS))
async def send_all_media(client, message):
    try:
        files, offset, total_results = await get_all_files(max_results=max_results)

        btn = [
            [
                InlineKeyboardButton(text=f"{file.file_name}", callback_data=f'send#{file.file_id}')
            ]
            for file in files
        ]

        btn.insert(MAX_BTTN, 
            [
                InlineKeyboardButton("! Sᴇɴᴅ Aʟʟ !", callback_data=f"get_all")
            ]
        )
        if offset:
            page_number = int(offset) // max_results
            btn.append([
                InlineKeyboardButton(text=f"📄 Page {page_number}/{math.ceil(total_results / max_results)}", callback_data="pages"),
                InlineKeyboardButton(text="Next", callback_data=f"pmnext_{offset}")
            ])
        else:
            btn.append(
                [
                    InlineKeyboardButton(text=f"📄 Page 1/1", callback_data="pages")
                ]
            )

        cap = f"Here are the {total_results} media files found in the database."

        abc = await message.reply_text(cap, quote=True, reply_markup=InlineKeyboardMarkup(btn))
    except Exception as e:
        # Handle exceptions by sending an error message
        error_message = f"An error occurred: {str(e)}"
        await query.message.reply_text(error_message)
        
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
        btn.insert(MAX_BTTN,
         [
            InlineKeyboardButton("! Sᴇɴᴅ Aʟʟ !", callback_data=f"get_all")
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
            btn.append([InlineKeyboardButton(text=f"📄 Page {page_number}/{math.ceil(total_results / max_results)}", callback_data="pages")])

        await query.edit_message_text(
            text=query.message.text.markdown,
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except Exception as e:
        # Handle exceptions by sending an error message
        error_message = f"An error occurred: {str(e)}"
        await query.message.reply_text(error_message)

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
        btn.insert(MAX_BTTN,
         [
            InlineKeyboardButton("! Sᴇɴᴅ Aʟʟ !", callback_data=f"get_all")
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
        # Handle exceptions by sending an error message
        error_message = f"An error occurred: {str(e)}"
        await query.message.reply_text(error_message)


@Client.on_callback_query(filters.regex(r'^send#'))
async def send_media_to_channel(client, query: CallbackQuery):
    try:
        file_id = query.data.split("#")[1]
        files_ = await get_file_details(file_id)
        
        if not files_:
            return await query.answer('No such file exists.')
        
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        
        # Send the selected media to the FILE_CHANNEL
        await client.send_cached_media(
            chat_id=FILE_DB_CHANNEL,
            file_id=file_id,
            caption=title,
        )
        
        await query.answer('Media sent to the channel.')
    except Exception as e:
        # Handle exceptions by sending an error message
        error_message = f"An error occurred: {str(e)}"
        await query.message.reply_text(error_message)

@Client.on_callback_query(filters.regex(r'^get_all'))
async def send_all_media_to_channel(client, query: CallbackQuery):
    try:
        offset_str = query.data.split("_")[1] if "_" in query.data else "0"
        offset = int(offset_str) if offset_str.isdigit() else 0
        files, _, total_results = await get_all_files(max_results=max_results, offset=int(offset))
        
        if not files:
            return await query.answer('No files found on this page.')
        else:
            total_files = len(files)
            total_sent = 0
            total_invalid = 0
            status_message = f"Total Files: {total_files}. Sending process started."
            status = await query.message.reply_text(status_message)

        for i in range(0, len(files), BATCH_SIZE):
            batch = files[i:i+BATCH_SIZE]
            for file in batch:
                try:
                    await client.send_cached_media(
                        chat_id=FILE_DB_CHANNEL,
                        file_id=file.file_id,
                        caption=file.file_name,
                    )
                    total_sent += 1
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    continue
                except PeerIdInvalid:
                    total_invalid += 1
                    continue
                except MediaEmpty as me:
                    total_invalid += 1
                    continue
                except Exception as e:
                    total_invalid += 1
                    error_message = f"An error occurred: {str(e)}"
                    logger.error(error_message)
                    await query.message.reply_text(error_message)
                    continue
            await asyncio.sleep(SEND_INTERVAL)
            status_update = f"Total Files: {total_files}\nSent: {total_sent}\nInvalid: {total_invalid}"
            await status.edit_text(status_update)

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        logger.error(error_message)
        await query.message.reply_text(error_message)
        
