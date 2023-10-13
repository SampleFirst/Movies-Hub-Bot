from pyrogram import Client, filters
import requests
import os

@Client.on_message(filters.command("insta"))
async def download_instagram_post(client, message):
    if len(message.command) > 1:
        instagram_link = message.command[1]

        try:
            response = requests.get(instagram_link)

            if "/p/" in instagram_link:
                file_extension = "jpg"
                file_name = f"downloaded_post.{file_extension}"

                # Save the downloaded image
                with open(file_name, "wb") as image_file:
                    image_file.write(response.content)

                chat_id = message.chat.id

                # Send the downloaded image with best quality
                await client.send_photo(
                    chat_id=chat_id,
                    photo=file_name,
                    caption=f"**ᴛɪᴛʟᴇ :** []()\n**ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {message.from_user.mention}",
                    supports_streaming=True,
                )

                os.remove(file_name)

            elif "/reel/" in instagram_link:
                file_extension = "mp4"
                file_name = f"downloaded_reel.{file_extension}"

                # Save the downloaded video
                with open(file_name, "wb") as video_file:
                    video_file.write(response.content)

                chat_id = message.chat.id

                # Send the downloaded video with best quality
                await client.send_video(
                    chat_id=chat_id,
                    video=file_name,
                    caption=f"**ᴛɪᴛʟᴇ :** []()\n**ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {message.from_user.mention}",
                    supports_streaming=True,
                )

                os.remove(file_name)

            else:
                await message.reply_text("Unknown Instagram post type.")
        except Exception as e:
            await message.reply_text(f"Error: {str(e)}")
    else:
        await message.reply_text("Please provide an Instagram post link with the command.")

