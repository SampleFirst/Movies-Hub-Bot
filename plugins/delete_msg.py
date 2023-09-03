from pyrogram import Client, filters
import re


# Define the delete_msg command handler
@Client.on_message(filters.private & filters.command("delete_message"))
async def delete_messages_command(client, message):
    try:
        # Extract the chat ID and number of messages from the command
        command_parts = message.text.split()
        if len(command_parts) != 3:
            await message.reply("Invalid command format. Use /delete_message <channel_message_link> <num_messages>")
            return

        channel_message_link = command_parts[1]
        num_messages = int(command_parts[2])

        # Extract the chat ID from the message link using regular expressions
        match = re.match(r"https://t\.me/.+?/(\d+)", channel_message_link)
        if not match:
            await message.reply("Invalid channel message link format.")
            return

        chat_id = int(match.group(1))

        # Delete the specified number of messages in the chat
        await client.delete_messages(chat_id, list(range(message.message_id + 1, message.message_id + 1 + num_messages)))
        await message.reply(f"{num_messages} messages deleted successfully.")
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")
