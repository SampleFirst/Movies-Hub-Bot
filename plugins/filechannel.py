from pyrogram import Client, filters
from pyrogram.types import InputMediaDocument
from database.ia_filterdb import get_search_results
from info import ADMINS, FILE_DB_CHANNEL
import asyncio

# Define a command handler
@Client.on_message(filters.command("sendallmedia") & filters.user(ADMINS))
async def send_all_media(client, message):

    # Query the database to get all media files (Assuming the get_search_results function is defined elsewhere)
    files, _, _ = await get_search_results("", max_results=None)

    if not files:
        await message.reply("No media files found in the database.")
        return

    batch_size = 100  # Number of media files to send in each batch
    total_files = len(files)

    for i in range(0, total_files, batch_size):
        batch = files[i:i + batch_size]
        batch_info = []

        for media in batch:
            file_id = media.file_id
            caption = media.caption if media.caption else ""
            await client.send_media(
                chat_id=FILE_DB_CHANNEL,
                media=InputMediaDocument(file_id),
                caption=caption
            )

            # Collect information for the batch
            file_name = media.file_name
            file_size = media.file_size
            batch_info.append(f"Name: {file_name}, Size: {file_size} bytes")

        # Create a .txt file for the batch
        batch_info_txt = "\n".join(batch_info)
        file_name = f"batch_{i // batch_size + 1}_info.txt"
        with open(file_name, "w") as file:
            file.write(batch_info_txt)

        # Send the .txt file to the admins
        for admin in ADMINS:
            await client.send_document(admin, document=file_name)

        await asyncio.sleep(2)  # Wait for 2 seconds before sending the next batch

    await message.reply("All media files have been sent to the 'FILE_DB_CHANNEL.'")
