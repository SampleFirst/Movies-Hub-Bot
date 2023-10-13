from pyrogram import Client, filters
from pyrogram.types import Message
import requests
import os

@Client.on_message(filters.command("insta"))
def download_instagram_post(client, message):
    # Get the Instagram post link from the command arguments
    if len(message.command) > 1:
        instagram_link = message.command[1]

        # Add "dd" before "instagram"
        modified_link = instagram_link.replace("://www.instagram.com", "://www.ddinstagram.com")

        # Download the Instagram post
        try:
            response = requests.get(modified_link)

            # Check if the post contains images or videos
            if "image" in response.headers["content-type"]:
                file_extension = "jpg"
            elif "video" in response.headers["content-type"]:
                file_extension = "mp4"
            else:
                message.reply_text("Unsupported content type. Unable to download.")
                return

            # Save the content to a file
            file_name = f"downloaded_post.{file_extension}"
            with open(file_name, "wb") as file:
                file.write(response.content)

            # Send the downloaded file as a document
            if file_extension == "jpg":
                message.reply_photo(photo=file_name, caption="Post downloaded successfully!")
            elif file_extension == "mp4":
                message.reply_video(video=file_name, caption="Post downloaded successfully!")

            # Remove the temporary file
            os.remove(file_name)

        except Exception as e:
            message.reply_text(f"Error: {str(e)}")
    else:
        message.reply_text("Please provide an Instagram post link with the command.")
