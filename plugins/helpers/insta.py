from pyrogram import Client, filters
from pyrogram.types import Message
import instaloader


def download_and_send_media(url, chat_id):
    L = instaloader.Instaloader()

    try:
        post = instaloader.Post.from_shortcode(L.context, url)
        if post.is_video:
            video_path = f"{post.owner_username}_{post.shortcode}.mp4"
            L.download_post(post, target=video_path, post_filter=lambda _: _.is_video)
            Client.send_video(chat_id, video_path)
        else:
            image_path = f"{post.owner_username}_{post.shortcode}.jpg"
            L.download_post(post, target=image_path, post_filter=lambda _: not _.is_video)
            Client.send_photo(chat_id, image_path)
    except Exception as e:
        Client.send_message(chat_id, f"Error: {str(e)}")


@Client.on_message(filters.command("sendpost"))
def send_post(client: Client, message: Message):
    if message.reply_to_message and message.reply_to_message.text:
        url = message.reply_to_message.text
    else:
        url = message.text.split(" ", 1)[1]

    download_and_send_media(url, message.chat.id)

