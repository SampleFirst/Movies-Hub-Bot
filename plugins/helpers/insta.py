from pyrogram import Client, filters
import requests

@Client.on_message(filters.command("download"))
async def download_instagram_post(client, message):
    # Get the Instagram post link from the command arguments
    if len(message.command) > 1:
        instagram_link = message.command[1]

        # Add "dd" before "instagram"
        modified_link = instagram_link.replace("://www.instagram.com", "://www.ddinstagram.com")

        # Download the Instagram post
        try:
            response = requests.get(modified_link)
            
            # Process the response or save the content as needed
            # For example, you can save it to an "Images" folder
            file_name = "downloaded_post.jpg"
            with open(file_name, "wb") as file:
                file.write(response.content)
            
            # Send the downloaded file as an image
            await client.send_photo(
                chat_id=message.chat.id,
                photo=open(file_name, "rb"),
                caption="Post downloaded successfully!"
            )
        except Exception as e:
            await message.reply_text(f"Error: {str(e)}")
    else:
        await message.reply_text("Please provide an Instagram post link with the command.")
