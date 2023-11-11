import asyncio
import math
import logging
from pyrogram.errors import MessageNotModified
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, PeerIdInvalid
from pyrogram import Client, filters
from database.ia_filterdb import Media, get_all_media, get_file_details
from info import ADMINS, FILE_DB_CHANNEL
from utils import get_size


BATCH_SIZE = 5  # Number of media files to send in each batch
SEND_INTERVAL = 10  # Time interval (in seconds) between batches

# Logging Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



@Client.on_message(filters.command("get_out") & filters.user(ADMINS))
async def send_all_media_on(client, message):
    try:
        files, offset, total_results = await get_all_media(offset=offset)
        
        if not files:
            return await query.answer('No files found on this page.')
        else:
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
        
