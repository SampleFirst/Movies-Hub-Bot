from pyrogram import Client, filters
from instaloader import Instaloader, Post

@Client.on_message(filters.command("insta"))
async def instagram_download(client, message):
    try:
        # Get the Instagram reel link from the command
        command_parts = message.text.split(" ", 1)

        if len(command_parts) == 2:
            reel_link = command_parts[1]

            # Ensure it's a valid Instagram Reels link
            if "instagram.com/reel/" in reel_link:
                # Download the reel using Instaloader
                insta_loader = Instaloader()

                # Extracting Post ID from the Reels link
                post_id = reel_link.split("/")[-1]

                # Download the post
                post = Post.from_shortcode(insta_loader.context, post_id)
                insta_loader.download_post(post, target='Reels')

                # Send the downloaded video to the user
                video_path = f"Reels/{post.date_utc.strftime('%Y%m%d_%H%M%S')}_{post_id}.mp4"
                caption = f"Instagram Reels Download\nLink: {reel_link}"
                await client.send_video(
                    chat_id=message.chat.id,
                    video=video_path,
                    caption=caption,
                )
            else:
                await message.reply_text("Please provide a valid Instagram Reels link.")
        else:
            await message.reply_text("Please provide a valid Instagram Reels link.")

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        await message.reply_text(error_message)
