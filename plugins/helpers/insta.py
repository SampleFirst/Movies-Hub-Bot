import os
import asyncio
import instaloader
from pyrogram import filters, Client
from pyrogram.types import Message

# Create an Instaloader instance
loader = instaloader.Instaloader()

# Command handler for /insta
@Client.on_message(filters.command("insta") & filters.private)
async def download_instagram_media(client, message: Message):
    # Get the Instagram media URL from the command arguments
    if len(message.command) != 2:
        await message.reply("Invalid command syntax. Usage: /insta [media_url]")
        return

    media_url = message.command[1]

    try:
        # Download the media file
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, "media")

        loader.download([media_url], target=file_path)

        # Determine the file type
        file_extension = os.path.splitext(file_path)[1]

        # Send the media file as a file in a private message
        if file_extension == ".mp4":
            await client.send_video(
                chat_id=message.from_user.id,
                video=file_path,
                caption="Here's the Instagram reel you requested."
            )
        elif file_extension in [".jpg", ".jpeg"]:
            await client.send_photo(
                chat_id=message.from_user.id,
                photo=file_path,
                caption="Here's the Instagram photo you requested."
            )
        else:
            await message.reply("Unsupported media type.")

        # Remove the downloaded media file
        os.remove(file_path)

    except Exception as e:
        await message.reply(f"Error: {str(e)}")
