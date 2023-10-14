from pyrogram import Client, filters
import aiohttp
from io import BytesIO

# Command handler for downloading Instagram posts
@Client.on_message(filters.command("download"))
async def download_instagram_post(client, message):
    # Check if the command includes an Instagram post link
    if len(message.command) > 1:
        instagram_link = message.command[1]

        # Modify the link for downloading
        modified_link = instagram_link.replace("://www.instagram.com", "://www.ddinstagram.com")

        try:
            # Use aiohttp for asynchronous HTTP requests
            async with aiohttp.ClientSession() as session:
                async with session.get(modified_link) as response:
                    # Check if the response is successful
                    if response.status == 200:
                        # Read the content and send it as a photo
                        content = await response.read()
                        file_bytes = BytesIO(content)
                        file_bytes.name = "downloaded_post.jpg"  # You can adjust the file name and extension
                        await client.send_photo(
                            chat_id=message.chat.id,
                            photo=file_bytes,
                            caption="Post downloaded successfully!"
                        )
                    else:
                        await message.reply_text(f"Failed to download the Instagram post. Status Code: {response.status}")
        except Exception as e:
            await message.reply_text(f"Error: {str(e)}")
    else:
        await message.reply_text("Please provide an Instagram post link with the command.")
