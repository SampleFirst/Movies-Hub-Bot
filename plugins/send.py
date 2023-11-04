from pyrogram import Client, filters
from database.ia_filterdb import Media, get_all_files
from info import ADMINS, FILE_CHANNEL, MAX_BTTN 
import time
import asyncio

max_results = MAX_BTTN

# Define your command handler
@Client.on_message(filters.command("sendfiles") & filters.user(ADMINS))
async def send_saved_files(client, message):
    chat_id = message.chat.id

    offset = 0
    total_sent_files = 0
    batch_count = 0

    start_time = time.time()

    while True:
        files, next_offset, total_results = await get_all_files(max_results=max_results, offset=offset)

        if not files:
            break

        batch_count += 1
        total_sent_files += len(files)

        await client.send_message(
            chat_id,
            f"Batch {batch_count}: Sending {len(files)} files, Total Sent Files: {total_sent_files}",
        )

        for file in files:
            await bot.send_cached_media(
                chat_id=FILE_CHANNEL,
                file_id=file.file_id,
                caption=file.file_name
                )
            
        await asyncio.sleep(60)  # Sleep for 60 seconds between batches

        offset = next_offset

    end_time = time.time()
    elapsed_time = end_time - start_time

    await client.send_message(
        chat_id,
        f"All batches sent. Total Sent Files: {total_sent_files}, Total Batches: {batch_count}, Elapsed Time: {elapsed_time} seconds",
    )

    # Create and send the .txt file with file information
    txt_file_content = "\n\n".join(file_info_list)
    with open("file_info.txt", "w") as txt_file:
        txt_file.write(txt_file_content)

    await client.send_document(chat_id, "file_info.txt")
