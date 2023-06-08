import os
import asyncio
import instaloader
import requests
from pyrogram import filters, Client
from pyrogram.types import Message
from pathlib import Path



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
        
        response = requests.get(media_url, stream=True)
        response.raise_for_status()
        
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        
        # Determine the file type
        file_extension = Path(file_path).suffix
        
        # Send the media file as a file in a private message
        if file_extension == ".mp4":
            await client.send_video(
                chat_id=message.from_user.id,
                video=file_path,
                caption="Here's the Instagram reel you requested."
            )
        elif file_extension == ".jpg" or file_extension == ".jpeg":
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

