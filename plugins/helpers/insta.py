from pyrogram import Client, filters
from pyrogram.types import Message
import requests
from io import BytesIO
from PIL import Image

@Client.on_message(filters.command("download"))
def download_instagram_post(client, message):
    # Get the Instagram post link from the command arguments
    if len(message.command) > 1:
        instagram_link = message.command[1]

        # Add "dd" before "instagram"
        modified_link = instagram_link.replace("://www.instagram.com", "://www.ddinstagram.com")

        # Download the Instagram post
        try:
            response = requests.get(modified_link)

            # Process the response and save as an image
            image = Image.open(BytesIO(response.content))
            image_file_name = "downloaded_post.jpg"
            image.save(image_file_name, "JPEG")

            # Send the downloaded image as a document
            message.reply_document(document=image_file_name, caption="Post downloaded successfully!")
        except Exception as e:
            message.reply_text(f"Error: {str(e)}")
    else:
        message.reply_text("Please provide an Instagram post link with the command.")


