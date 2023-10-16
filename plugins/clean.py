import asyncio
from pyrogram import Client, filters

COUNT_MESSAGES = 0

@Client.on_message((filters.group) & filters.text & filters.incoming)
async def count_messages_and_delete(client, message):
    global COUNT_MESSAGES

    group_id = message.chat.id
    
    # Increment the COUNT_MESSAGES variable
    COUNT_MESSAGES += 1
    
    # Check if the count has reached 10
    if COUNT_MESSAGES == 10:
        status_message = await client.send_message(group_id, "Deleting Messages...")

        message_ids = []

        # Get the last 10 messages in the group
        async for hist_message in client.iter_chat_messages(chat_id=group_id, limit=10):
            message_ids.append(hist_message.message_id)

        # Delete the last 10 messages
        await client.delete_messages(chat_id=group_id, message_ids=message_ids, revoke=True)

        await status_message.edit_text("Deleted 10 messages")
        COUNT_MESSAGES = 0  # Reset the count after deletion

        await asyncio.sleep(5)  # Wait for 5 seconds before deleting the status message
        await status_message.delete()

    await message.delete()
