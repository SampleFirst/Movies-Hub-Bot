from pyrogram import Client, filters
from info import CHANNELS
from database.ia_filterdb import save_file

media_filter = filters.document | filters.video | filters.audio


@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    """Media Handler"""
    file_types = ["document", "video", "audio"]
    media_files = []

    for file_type in file_types:
        media = getattr(message, file_type, None)
        if media is not None:
            media.file_type = file_type
            media.caption = message.caption
            media_files.append(media)

    if len(media_files) == 0:
        return

    # Sort media files by name in descending order
    media_files.sort(key=lambda x: x.file_name, reverse=True)

    for media in media_files:
        await save_file(media)
