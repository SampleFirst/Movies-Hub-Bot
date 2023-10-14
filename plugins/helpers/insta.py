from pyrogram import Client, filters
from pyrogram.types import Message
import requests
import aiohttp
from io import BytesIO

@Client.on_message(filters.command("download"))
async def download_instagram_post(client, message):
    # Get the Instagram post link from the command arguments
    if len(message.command) > 1:
        instagram_link = message.command[1]

        # Add "dd" before "instagram"
        modified_link = instagram_link.replace("://www.instagram.com", "://www.ddinstagram.com")

        # Download the Instagram post
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(modified_link) as response:
                    # Check if the response is successful
                    if response.status == 200:
                        # Read the content and send it as a photo
                        content = await response.read()
                        file_bytes = BytesIO(content)
                        file_bytes.name = "downloaded_post.jpg"  # You can adjust the file name and extension
                        await message.reply_photo(
                            photo=file_bytes,
                            caption="Post downloaded successfully!"
                        )
                    else:
                        await message.reply_text(f"Failed to download the Instagram post. Status Code: {response.status}")
        except Exception as e:
            await message.reply_text(f"Error: {str(e)}")
    else:
        await message.reply_text("Please provide an Instagram post link with the command.")
