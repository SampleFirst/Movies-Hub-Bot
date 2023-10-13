from pyrogram import Client, filters
import requests
import os

@Client.on_message(filters.command("insta"))
async def download_instagram_post(client, message):
    # Get the Instagram post link from the command arguments
    if len(message.command) > 1:
        instagram_link = message.command[1]

        # Download the Instagram post
        try:
            response = requests.get(instagram_link)

            # Check if it's an image or a reel
            if "/p/" in instagram_link:
                # It's a post
                file_extension = "jpg"
                file_name = f"downloaded_post.{file_extension}"
                copy = f"**ᴛɪᴛʟᴇ :** []()\n**ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {message.from_user.mention}"

                # Save the downloaded image
                with open(file_name, "wb") as image_file:
                    image_file.write(response.content)
                
                await client.send_photo(
                    photo=open(file_name, "rb"),
                    caption=copy,
                )

                # Remove the temporary file after sending
                os.remove(file_name)

            elif "/reel/" in instagram_link:
                # It's a reel
                file_extension = "mp4"
                file_name = f"downloaded_reel.{file_extension}"
                copy = f"**ᴛɪᴛʟᴇ :** []()\n**ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {message.from_user.mention}"

                # Save the downloaded video
                with open(file_name, "wb") as video_file:
                    video_file.write(response.content)

                # Send the downloaded video as a document
                await client.send_video(
                    video=open(file_name, "rb"),
                    caption=copy,
                    supports_streaming=True,
                )

                # Delete the downloaded file
                os.remove(file_name)
            else:
                # Unknown post type
                await message.reply_text("Unknown Instagram post type.")
        except Exception as e:
            await message.reply_text(f"Error: {str(e)}")
    else:
        await message.reply_text("Please provide an Instagram post link with the command.")

