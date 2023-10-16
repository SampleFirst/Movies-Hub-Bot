from pyrogram import Client, filters
import asyncio
from info import ADMINS, YOUR_GROUP_ID

TIME = 100

@Client.on_message(filters.chat("YOUR_GROUP_ID"))
async def delete_message(client, message):
    try:
        if message.from_user.id in ADMINS:
            return
        else:
            await asyncio.sleep(TIME)
            await client.delete_messages(message.chat.id, message.message_id)
    except Exception as e:
        print(e)
      
