from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid
from database.ia_filterdb import Media, get_all_files
from info import ADMINS, FILE_CHANNEL, MAX_BTTN, CUSTOM_FILE_CAPTION
import time
import asyncio
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

max_results = MAX_BTTN


# Define your command handler
@Client.on_message(filters.command("sendfiles") & filters.user(ADMINS))
async def send_saved_files(client, message):
    chat_id = message.chat.id

    offset = 0
    total_sent_files = 0
    batch_count = 0
    file_info_list = []

    start_time = time.time()

    while True:
        files, offset, total_results = await get_all_files(max_results=max_results)

        if not files:
            break

        batch_count += 1
        total_sent_files += len(files)

        await message.reply_text(
            f"Batch {batch_count}: Sending {len(files)} files, Total Sent Files: {total_sent_files}"
        )

        for file in files:
            f_caption = file.caption
            title = file.file_name
            size = file.file_size

            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption = CUSTOM_FILE_CAPTION.format(
                        file_name=title if title else "Untitled",
                        file_size=size if size else "Unknown",
                        file_caption=f_caption if f_caption else "",
                    )
                except Exception as e:
                    logger.error(f"Error while formatting caption: {e}")

            if f_caption is None:
                f_caption = title if title else "Untitled"

            try:
                await client.send_cached_media(
                    chat_id=FILE_CHANNEL,
                    file_id=file.file_id,
                    caption=f_caption
                )
            except PeerIdInvalid:
                logger.error("Error: Peer ID is invalid!")
                await message.reply_text("Peer ID is invalid!")
                return
            except Exception as e:
                logger.error(f"Error: {e}")
                await message.reply_text(f"Error: {e}")

            file_info_list.append(f"File Name: {title}, File Size: {size}, Caption: {f_caption}")

        await asyncio.sleep(60)  # Sleep for 60 seconds between batches

        offset = next_offset

    end_time = time.time()
    elapsed_time = end_time - start_time

    await message.reply_text(
        f"All batches sent. Total Sent Files: {total_sent_files}, Total Batches: {batch_count}, Elapsed Time: {elapsed_time} seconds"
    )

    # Create and send the .txt file with file information
    txt_file_content = "\n\n".join(file_info_list)
    with open("file_info.txt", "w") as txt_file:
        txt_file.write(txt_file_content)

    await message.reply_document("file_info.txt")
