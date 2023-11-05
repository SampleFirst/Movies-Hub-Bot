from pyrogram import Client, filters
from info import FILE_DB_CHANNEL
from database.ia_filterdb import Media, get_all_saved_media


# Define a command handler for your new command
@Client.on_message(filters.command("send_all_media"))
async def send_all_media_command(client, message):
    try:
        files = await get_all_saved_media()

        if not files:
            await message.reply("No saved media found.")
        else:
            for file in files:
                try:
                    await bot.send_cached_media(
                        chat_id=FILE_DB_CHANNEL,
                        file_id=file.file_id,
                        caption=file.caption,
                    )
                except Exception as e:
                    print(f"Error sending media: {str(e)}")
                    continue
                    
        await message.reply("All saved media files have been sent to the channel.")
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")
        
