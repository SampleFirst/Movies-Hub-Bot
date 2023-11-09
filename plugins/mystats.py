from pyrogram import Client, filters
from pyrogram.types import Message
from database.ia_filterdb import Media, get_all_media_files
import asyncio
from info import ADMINS, FILE_DB_CHANNEL 


# Command to send all saved media in the database to the FILE_CHANNEL
@Client.on_message(filters.command("send_all") & filters.private)
async def send_all_media(bot, message):
    if message.from_user.id not in ADMINS:
        return 

    files = await get_all_media_files()
    
    for file in files:
        f_caption = file.caption
        title = file.file_name
        size = get_size(file.file_size)

        if f_caption is None:
            f_caption = f"{title}"

        try:
            await bot.send_cached_media(
                chat_id=FILE_DB_CHANNEL,
                file_id=file.file_id,
                caption=f_caption,
                protect_content=False,
            )

        except PeerIdInvalid:
            logger.error("Error: Peer ID Invalid!")
            return "Peer ID Invalid!"
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"

    return 'done'
