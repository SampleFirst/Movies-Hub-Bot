from pyrogram import Client, filters
from pyrogram.types import Message
import instaloader



def download_media(media_url):
    loader = instaloader.Instaloader()

    try:
        post = instaloader.Post.from_shortcode(loader.context, media_url)
        for node in post.get_sidecar_nodes():
            if node.is_video:
                loader.download_post(post, target=node.url, filename='video')
            elif node.is_image:
                loader.download_post(post, target=node.url, filename='image')
    except Exception as e:
        print(f"Error: {e}")


@Client.on_message(filters.command("download"))
def download_command(client, message):
    if len(message.command) == 2:
        media_url = message.command[1]
        download_media(media_url)
        client.send_message(
            chat_id=message.chat.id,
            text="Media downloaded successfully!",
        )
    else:
        client.send_message(
            chat_id=message.chat.id,
            text="Please provide a valid Instagram post or reel link.",
        )

@Client.on_message(filters.command("modifylink"))
def modify_instagram_link(client: Client, message: Message):
    # Extract the Instagram post link from the command
    original_link = message.text.split(" ", 1)[1].strip()

    # Modify the link by adding "dd" before "instagram"
    modified_link = original_link.replace("instagram", "ddinstagram")

    # Send back the modified link
    client.send_message(
        chat_id=message.chat.id,
        text=f"Modified Instagram Post Link: {modified_link}",
    )

    # Check if the modified link contains "instagram" to identify it as an image post
    if "instagram" in modified_link:
        # Assuming you have the image file path or URL, replace 'image_path_or_url' with the actual path or URL
        image_path_or_url = 'image_path_or_url'

        # Send the image
        client.send_photo(
            chat_id=message.chat.id,
            photo=image_path_or_url,
            caption="Modified Instagram Post Image",
        )
