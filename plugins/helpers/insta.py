from pyrogram import Client, filters
import requests

@Client.on_message(filters.command("download"))
def download_instagram_post(client, message):
    try:
        # Extracting the original link from the message
        original_link = message.text.split()[1]

        # Modifying the link for extraction
        modified_link = original_link.replace("www.instagram.com", "www.ddinstagram.com")

        # Fetch HTML content to extract image URL
        response = requests.get(modified_link)
        response.raise_for_status()  # Check for request errors

        # Extract image URL from HTML content using JSON parsing
        json_data = response.json()
        image_url = json_data["graphql"]["shortcode_media"]["display_url"]

        # Download the image
        image_response = requests.get(image_url)
        image_response.raise_for_status()  # Check for request errors

        # Save the image
        with open("downloaded_image.jpg", "wb") as image_file:
            image_file.write(image_response.content)

        # Send the image back to the user
        message.reply_photo("downloaded_image.jpg")

    except Exception as e:
        # Handle any exceptions and inform the user
        message.reply_text(f"An error occurred: {str(e)}")
