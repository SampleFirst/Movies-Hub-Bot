from pyrogram import Client, filters
import instaloader


@Client.on_message(filters.command("insta"))
async def instagram_download(client, message):
    try:
        # Get the Instagram reel link from the command
        reel_link = message.text.split(" ", 1)[1]

        # Download the reel using instaloader
        insta_loader = instaloader.Instaloader()
        insta_loader.download_reels([reel_link], download_pictures=False)

        # Send the downloaded video to the user
        video_path = f"{reel_link.split('/')[-2]}_{reel_link.split('/')[-1]}.mp4"
        await message.reply_video(video_path)

    except IndexError:
        await message.reply_text("Please provide a valid Instagram Reels link.")
