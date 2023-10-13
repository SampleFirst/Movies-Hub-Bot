from pyrogram import Client, filters
from pyrogram.types import Message
import requests
from bs4 import BeautifulSoup
import os

@Client.on_message(filters.command("insta"))
def download_instagram_post(client, message):
    # Get the Instagram post link from the command arguments
    if len(message.command) > 1:
        instagram_link = message.command[1]

        # Fix the link modification
        modified_link = instagram_link.replace("://www.instagram.com", "://www.ddinstagram.com")

        # Download the Instagram post
        try:
            response = requests.get(modified_link)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Check if the post is a video
            video_tag = soup.find('meta', property='og:video')
            if video_tag:
                video_url = video_tag['content']
                # Download the video
                video_response = requests.get(video_url)
                video_file_name = "downloaded_post.mp4"
                with open(video_file_name, "wb") as video_file:
                    video_file.write(video_response.content)
                message.reply_video(video_file_name, caption="Post video downloaded successfully!")

            # Check if the post is an image
            else:
                image_tag = soup.find('meta', property='og:image')
                if image_tag:
                    image_url = image_tag['content']
                    # Download the image
                    image_response = requests.get(image_url)
                    image_file_name = "downloaded_post.jpg"
                    with open(image_file_name, "wb") as image_file:
                        image_file.write(image_response.content)
                    message.reply_photo(image_file_name, caption="Post image downloaded successfully!")

            # Remove the temporary files
            if 'video_file_name' in locals():
                os.remove(video_file_name)
            if 'image_file_name' in locals():
                os.remove(image_file_name)

        except Exception as e:
            message.reply_text(f"Error: {str(e)}")
    else:
        message.reply_text("Please provide an Instagram post link with the command.")
