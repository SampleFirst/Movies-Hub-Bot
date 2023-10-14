from pyrogram import Client, filters
from pyrogram.types import Message
import requests
import aiohttp

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
                    # Process the response or save the content as needed
                    # For example, you can save it to a file
                    file_name = "downloaded_post.html"
                    with open(file_name, "wb") as file:
                        file.write(await response.read())
                    # Send the downloaded file as a document
                    await message.reply_photo(
                        photo=file_name,
                        caption="Post downloaded successfully!"
                    )
        except Exception as e:
            await message.reply_text(f"Error: {str(e)}")
    else:
        await message.reply_text("Please provide an Instagram post link with the command.")
