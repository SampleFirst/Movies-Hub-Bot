from pyrogram import Client, filters
import requests
import os
import re

@Client.on_message(filters.command("insta"))
async def download_instagram_post(client, message):
    if len(message.command) > 1:
        instagram_link = message.command[1]

        try:
            response = requests.get(instagram_link)

            # Extract post shortcode from the link
            shortcode_match = re.search(r"/p/([^/?]+)|/reel/([^/?]+)", instagram_link)
            if shortcode_match:
                shortcode = shortcode_match.group(1) or shortcode_match.group(2)

                if "/p/" in instagram_link:
                    file_extension = "jpg"
                    file_name = f"downloaded_post_{shortcode}.{file_extension}"

                    # Save the downloaded image
                    with open(file_name, "wb") as image_file:
                        image_file.write(response.content)

                    chat_id = message.chat.id

                    # Send the downloaded image with best quality
                    await client.send_photo(
                        chat_id=chat_id,
                        photo=file_name,
                        caption=f"**ᴛɪᴛʟᴇ :** []()\n**ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {message.from_user.mention}",
                    )

                    os.remove(file_name)

                elif "/reel/" in instagram_link:
                    file_extension = "mp4"
                    file_name = f"downloaded_reel_{shortcode}.{file_extension}"

                    # Save the downloaded video
                    with open(file_name, "wb") as video_file:
                        video_file.write(response.content)

                    chat_id = message.chat.id

                    # Send the downloaded video with best quality
                    await client.send_video(
                        chat_id=chat_id,
                        video=file_name,
                        caption=f"**ᴛɪᴛʟᴇ :** []()\n**ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {message.from_user.mention}",
                    )

                    os.remove(file_name)

                else:
                    await message.reply_text("Unknown Instagram post type.")
            else:
                await message.reply_text("Invalid Instagram link.")
        except Exception as e:
            await message.reply_text(f"Error: {str(e)}")
    else:
        await message.reply_text("Please provide an Instagram post or reel link with the command.")
