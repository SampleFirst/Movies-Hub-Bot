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

            # Check if it's an image or a reel
            if "/p/" in modified_link:
                # It's a post
                file_extension = "jpg"
                file_name = f"downloaded_post.{file_extension}"

                # Save the content to a file
                with open(file_name, "wb") as file:
                    file.write(response.content)

                # Send the downloaded image as a photo
                with open(file_name, "rb") as photo_file:
                    message.reply_photo(photo=photo_file, caption="Post downloaded successfully!")

                # Remove the temporary file after sending
                os.remove(file_name)

            elif "/reel/" in modified_link:
                # It's a reel
                file_extension = "mp4"
                file_name = f"downloaded_reel.{file_extension}"

                # Save the content to a file
                with open(file_name, "wb") as file:
                    file.write(response.content)

                # Send the downloaded video as a document
                with open(file_name, "rb") as video_file:
                    message.reply_video(video=video_file, caption="Reel downloaded successfully!")

                # Remove the temporary file after sending
                os.remove(file_name)

            else:
                # Unknown post type
                message.reply_text("Unknown Instagram post type.")
        except Exception as e:
            message.reply_text(f"Error: {str(e)}")
    else:
        message.reply_text("Please provide an Instagram post link with the command.")
