from pyrogram import Client
from pyrogram.types import Message


# Define the command handler
@Client.on_message(filters.command("deletelast") & filters.group)
await async def delete_last_100_messages(client, message):
    # Get the chat ID and last 100 messages
    chat_id = message.chat.id
    messages = await client.get_chat_history(chat_id, limit=100)

    # Extract message IDs
    message_ids = [msg.message_id for msg in messages]

    # Delete the last 100 messages
    await client.delete_messages(chat_id, message_ids)
