from pyrogram import Client, filters
from pyrogram.types import Message
from database.ia_filterdb import Media, get_files_from_channel
import asyncio
from info import ADMINS, FILE_DB_CHANNEL 


# Command to send all saved media in the database to the FILE_CHANNEL
@Client.on_message(filters.command("send_all_media"))
async def send_all_media_to_channel(_, message: Message):

    # Check if the user has the necessary permissions to run this command
    if user_id in ADMINS:
        # Get all saved media from the database
        saved_media, _ = await get_search_results(None, '', file_type=None, max_results=1000000, offset=0, filter=False)

        # Send each media to the FILE_CHANNEL
        for media in saved_media:
            file_id = media.file_id
            caption = media.caption
            file_name = media.file_name
            file_type = media.file_type
            mime_type = media.mime_type

            # Send the media to the channel
            try:
                await message.forward(FILE_DB_CHANNEL)
                await asyncio.sleep(1)  # Add a delay between sending each media
            except Exception as e:
                print(f"Error sending media: {e}")

        # Send a status message to the user
        await message.reply("All saved media sent to FILE_CHANNEL.")
    else:
        await message.reply("You do not have permission to run this command.")

