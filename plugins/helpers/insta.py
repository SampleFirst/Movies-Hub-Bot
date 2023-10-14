from pyrogram import Client, filters
import aiohttp
from io import BytesIO


# Command handler for downloading Instagram posts
@Client.on_message(filters.command("download"))
async def download_instagram_post(client, message):
    if len(message.command) > 1:
        instagram_link = message.command[1]
        modified_link = instagram_link.replace("://www.instagram.com", "://www.ddinstagram.com")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(modified_link) as response:
                    if response.status == 200:
                        content = await response.read()
                        file_bytes = BytesIO(content)

                        # Get file extension from response headers
                        content_type = response.headers.get('content-type', '').split('/')
                        file_extension = content_type[1] if len(content_type) == 2 else 'jpg'
                        
                        # Adjust the file name and extension
                        file_bytes.name = f"downloaded_post.{file_extension.lower()}"
                        
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


