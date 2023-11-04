from pyrogram import Client, filters
from info import FILE_CHANNEL  # Assuming you have defined FILE_CHANNEL in info.py
from database.ia_filterdb import Media, get_all_saved_media


# Define a command handler for your new command
@Client.on_message(filters.command("send_all_media"))
async def send_all_media_command(client, message):
    try:
        chat_id = FILE_CHANNEL  # Use the FILE_CHANNEL where you want to send the media
        files = await get_all_saved_media()

        if not files:
            await message.reply("No saved media found.")
        else:
            for file in files:
                try:
                    # Send each file to the specified channel
                    # You can customize this part based on your requirements
                    await client.send_cached_media(chat_id, file.file_id, caption=file.caption)
                except Exception as e:
                    print(f"Error sending media: {str(e)}")
                    continue  # Continue with the next file if there's an error

        await message.reply("All saved media files have been sent to the channel.")
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")
