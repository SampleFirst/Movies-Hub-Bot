from pyrogram import Client, filters
from pyrogram.types import Message
import requests

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
                # Process the response or save the content as needed
                # For example, you can save it to a file
                file_name = "downloaded_post.jpg"
                with open(file_name, "wb") as file:
                    file.write(response.content)
                # Send the downloaded image as a photo
                message.reply_photo(photo=file_name, caption="Post downloaded successfully!")
            elif "/reel/" in modified_link:
                # It's a reel
                # Process the response or save the content as needed
                # For example, you can save it to a file
                file_name = "downloaded_reel.mp4"
                with open(file_name, "wb") as file:
                    file.write(response.content)
                # Send the downloaded video as a document
                message.reply_video(video=file_name, caption="Reel downloaded successfully!")
            else:
                # Unknown post type
                message.reply_text("Unknown Instagram post type.")
        except Exception as e:
            message.reply_text(f"Error: {str(e)}")
    else:
        message.reply_text("Please provide an Instagram post link with the command.")

