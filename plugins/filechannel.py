import asyncio
import math
import logging
from pyrogram.errors import FloodWait, PeerIdInvalid
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.ia_filterdb import Media, get_all_files, get_file_details
from info import ADMINS, MAX_BTTN, FILE_DB_CHANNEL
from utils import get_size

# Define constants
MAX_BTNN = 5
BATCH_SIZE = 5
SEND_INTERVAL = 10

# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@Client.on_message(filters.command("getallmedia") & filters.user(ADMINS))
async def send_all_media(client, message):
    try:
        max_results = MAX_BTTN
        files, offset, total_results = await get_all_files(max_results=max_results)

        btn = [
            [
                InlineKeyboardButton(text=f"{file.file_name}", callback_data=f'send#{file.file_id}')
            ]
            for file in files
        ]

        btn.insert(MAX_BTTN,
            [
                InlineKeyboardButton("Send All", callback_data=f"send_all")
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

        await message.reply_text(cap, quote=True, reply_markup=InlineKeyboardMarkup(btn))
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        await message.reply_text(error_message)

@Client.on_callback_query(filters.regex(r'^pmnext_'))
async def next_page_button(client, query: CallbackQuery):
    try:
        offset = query.data.split("_")[1]
        max_results = MAX_BTTN
        files, new_offset, total_results = await get_all_files(max_results=max_results, offset=int(offset))
        page_number = int(offset) // max_results + 1

        btn = [
            [InlineKeyboardButton(text=f"{file.file_name}", callback_data=f'send#{file.file_id}')]
            for file in files
        ]

        btn.insert(MAX_BTTN,
            [
                InlineKeyboardButton("Send All", callback_data=f"send_all")
            ]
        )

        if new_offset:
            page_number = int(new_offset) // max_results + 1
            prev_offset = int(offset) - max_results

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

        await query.edit_message_text(
            text=query.message.text.markdown,
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        await query.message.reply_text(error_message)

@Client.on_callback_query(filters.regex(r'^pmprev_'))
async def prev_page_button(client, query: CallbackQuery):
    try:
        offset = query.data.split("_")[1]
        max_results = MAX_BTTN
        files, new_offset, total_results = await get_all_files(max_results=max_results, offset=int(offset))
        page_number = int(offset) // max_results + 1

        btn = [
            [InlineKeyboardButton(text=f"{file.file_name}", callback_data=f'send#{file.file_id}')]
            for file in files
        ]

        btn.insert(MAX_BTTN,
            [
                InlineKeyboardButton("Send All", callback_data=f"send_all")
            ]
        )

        if new_offset:
            page_number = int(new_offset) // max_results + 1
            prev_offset = int(offset) - max_results
            next_offset = int(offset) + max_results

            if prev_offset >= 0:
                btn.append([
                    InlineKeyboardButton(text="Previous", callback_data=f"pmprev_{prev_offset}"),
                    InlineKeyboardButton(text=f"📄 Page {page_number}/{math.ceil(total_results / max_results)}", callback_data="pages"),
                    InlineKeyboardButton(text="Next", callback_data=f"pmnext_{next_offset}"),
                ])
            elif next_offset < total_results:
                btn.append([
                    InlineKeyboardButton(text=f"📄 Page {page_number}/{math.ceil(total_results / max_results)}", callback_data="pages"),
                    InlineKeyboardButton(text="Next", callback_data=f"pmnext_{new_offset}")
                ])

        await query.edit_message_text(
            text=query.message.text.markdown,
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except Exception as e:
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

        # Send the selected media to the FILE_CHANNEL
        await client.send_cached_media(
            chat_id=FILE_DB_CHANNEL,
            file_id=file_id,
            caption=title,
        )

        await query.answer('Media sent to the channel.')
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        await query.message.reply_text(error_message)

@Client.on_callback_query(filters.regex(r'^send_all'))
async def send_all_media_to_channel(client, query: CallbackQuery):
    try:
        offset_str = query.data.split("_")[1] if "_" in query.data else "0"
        current_page = int(offset_str) if offset_str.isdigit() else 0
        offset = current_page * MAX_BTTN
        
        max_results = MAX_BTNN
        files, _, total_results = await get_all_files(max_results=max_results, offset=offset)

        if not files:
            return await query.answer('No files found on this page.')
        else:
            total_files = len(files)
            total_sent = 0
            total_invalid = 0
            left_files = total_files - total_sent - total_invalid
            status_message = f"Total Files: {total_files}. Sending process started."
            status = await query.message.reply_text(status_message)
    
        for i in range(0, len(files), BATCH_SIZE):
            batch = files[i:i + BATCH_SIZE]
            deleted = 0
            for file in batch:
                try:
                    await client.send_cached_media(
                        chat_id=FILE_DB_CHANNEL,
                        file_id=file.file_id,
                        caption=file.file_name,
                    )
                    total_sent += 1
                    result = await Media.collection.delete_one({
                        '_id': file.file_id,
                    })
                    if result.deleted_count:
                        deleted += 1
                except FloodWait as e:
                    await asyncio.sleep(e.seconds)
                    continue
                except PeerIdInvalid:
                    total_invalid += 1
                    continue
                except Exception as e:
                    total_invalid += 1
                    error_message = f"An error occurred: {str(e)}"
                    logger.error(error_message)
                    await query.message.reply_text(error_message)
                    continue
    
            await asyncio.sleep(SEND_INTERVAL)
            status_update = f"Total Files: {total_files}\nSent: {total_sent}\nInvalid: {total_invalid}\nTotal Deleted: {deleted}\nLeft Files: {left_files}"
            await status.edit_text(status_update)
    
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        logger.error(error_message)
        await query.message.reply_text(error_message)
    
