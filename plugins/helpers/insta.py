from pyrogram import Client, filters
from pyrogram.types import Message
import requests
import os

@Client.on_message(filters.command("insta"))
def download_instagram_post(client, message):
    if len(message.command) > 1:
        instagram_link = message.command[1]

        try:
            modified_link = modify_instagram_link(instagram_link)
            response = requests.get(modified_link)

            if "/p/" in modified_link:
                file_extension = "jpg"
                file_name = f"downloaded_post.{file_extension}"
                send_photo_response(message, response, file_name, "Post downloaded successfully!")

            elif "/reel/" in modified_link:
                file_extension = "mp4"
                file_name = f"downloaded_reel.{file_extension}"
                send_video_response(message, response, file_name, "Reel downloaded successfully!")

            else:
                message.reply_text("Unknown Instagram post type.")
        
        except Exception as e:
            message.reply_text(f"Error: {str(e)}")
    else:
        message.reply_text("Please provide an Instagram post link with the command.")

def modify_instagram_link(instagram_link):
    return instagram_link.replace("://www.instagram.com", "://www.ddinstagram.com")

def send_photo_response(message, response, file_name, caption):
    with open(file_name, "wb") as file:
        file.write(response.content)

    with open(file_name, "rb") as photo_file:
        message.reply_photo(photo=photo_file, caption=caption)

    os.remove(file_name)

def send_video_response(message, response, file_name, caption):
    with open(file_name, "wb") as file:
        file.write(response.content)

    with open(file_name, "rb") as video_file:
        message.reply_video(video=video_file, caption=caption)

    os.remove(file_name)
   
