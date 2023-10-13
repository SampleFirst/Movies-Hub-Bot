from pyrogram import Client, filters
import instaloader

@Client.on_message(filters.command("insta"))
async def instagram_download(client, message):
    try:
        # Get the Instagram reel link from the command
        command_parts = message.text.split(" ", 1)

        if len(command_parts) == 2:
            reel_link = command_parts[1]

            # Ensure it's a valid Instagram Reels link
            if "instagram.com/reel/" in reel_link:
                # Download the reel using instaloader
                insta_loader = instaloader.Instaloader()
                insta_loader.download_post(insta_loader, target='Reels')

                # Send the downloaded video to the user
                video_path = f"Reels/{reel_link.split('/')[-2]}_{reel_link.split('/')[-1]}.mp4"
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
