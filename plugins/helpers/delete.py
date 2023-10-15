from pyrogram import Client, filters
from pyrogram.types import Message

# Define the command handler
@Client.on_message(filters.command("deletelast"))
async def delete_last_messages(client, message):
    try:
        # Get the chat ID and last 100 messages
        chat_id = message.chat.id
        messages = []

        async for msg in client.iter_messages(chat_id, limit=100):
            messages.append(msg)

        # Check if there are messages to delete
        if messages:
            # Extract message IDs
            message_ids = [msg.message_id for msg in messages]

            # Delete the last 100 messages
            await client.delete_messages(chat_id, message_ids)
            await message.reply_text("Successfully deleted last 100 messages.")
        else:
            await message.reply_text("No messages found to delete.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")
