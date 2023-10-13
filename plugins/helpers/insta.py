import os
from pyrogram import Client, filters
import requests
from bs4 import BeautifulSoup
from pyrogram.types import InputMediaVideo, InputMediaPhoto


def get_instagram_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(response.text, "html.parser")

        video_url = soup.find("meta", property="og:video")["content"]
        image_url = soup.find("meta", property="og:image")["content"]

        return video_url, image_url

    except requests.RequestException as e:
        print(f"Error fetching Instagram content: {e}")
        return None, None


@Client.on_message(filters.command("insta"))
async def instagram_download(client, message):
    if len(message.command) == 2:
        url = message.command[1]
        video_url, image_url = get_instagram_content(url)

        if video_url and image_url:
            # Download video and image
            video_file = f"{url.split('/')[-1]}.mp4"
            image_file = f"{url.split('/')[-1]}.jpg"

            try:
                with open(video_file, "wb") as video, open(image_file, "wb") as image:
                    video.write(requests.get(video_url).content)
                    image.write(requests.get(image_url).content)

                # Send back the content
                media_group = [
                    InputMediaVideo(video_file, caption="Instagram Reel"),
                    InputMediaPhoto(image_file, caption="Instagram Post"),
                ]
                client.send_media_group(message.chat.id, media_group)

            except requests.RequestException as e:
                print(f"Error downloading content: {e}")

            finally:
                # Clean up downloaded files
                os.remove(video_file)
                os.remove(image_file)

        else:
            client.send_message(message.chat.id, "Failed to fetch Instagram content.")
