from pyrogram import Client, filters
from pyrogram.types import Message
from instaloader import Instaloader, Post

# Create an Instaloader instance
instaloader = Instaloader()

# Define a command handler for /sendpost
@Client.on_message(filters.command("sendpost"))
def send_post(client: Client, message: Message):
    # Get the Instagram post link from the command
    post_link = message.text.split(" ", 1)[1]

    try:
        # Get post details using Instaloader
        post = instaloader.get_post(post_link)
        
        # Process the post and send images or videos
        send_post_media(client, message.chat.id, post)
    except Exception as e:
        print(f"Error processing the Instagram post: {e}")
        client.send_message(message.chat.id, f"Error processing the Instagram post: {e}")

def send_post_media(client: Client, chat_id: int, post: Post):
    # Send images
    for index, image_url in enumerate(post.get_sidecar_nodes()):
        client.send_photo(chat_id, image_url.display_url, caption=f"Image {index + 1}")

    # Send videos
    if post.is_video:
        client.send_video(chat_id, post.video_url, caption="Video")
