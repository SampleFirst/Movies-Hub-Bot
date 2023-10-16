from pyrogram import Client, filters
import asyncio
from datetime import datetime, timedelta
import pytz
from info import YOUR_GROUP_ID

DELETE_MSG = "Deleting Messages..."

@Client.on_message(filters.chat(YOUR_GROUP_ID))
async def delete_messages_periodically(client, message):
    try:
        while True:
            await asyncio.sleep(300)  # 5 minutes interval

            # Get the current time in Kolkata timezone
            kolkata_timezone = pytz.timezone("Asia/Kolkata")
            current_time = datetime.now(kolkata_timezone)

            # Send a message every 5 minutes
            sent_message = await client.send_message(YOUR_GROUP_ID, DELETE_MSG)
            message_link = sent_message.link

            # Delete the last 100 messages
            messages = await client.get_chat_history(YOUR_GROUP_ID, limit=100)
            message_ids = [msg.message_id for msg in messages]
            await client.delete_messages(YOUR_GROUP_ID, message_ids)

            print(f"Deleted last 100 messages in {YOUR_GROUP_ID}.\nMessage link: {message_link}")

    except Exception as e:
        print(f"An error occurred: {e}")

