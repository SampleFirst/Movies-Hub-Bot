from pyrogram import Client, filters
from pyrogram.types import Message
from info import ADMINS 

maintenance_mode_enabled = False

@Client.on_message(filters.command("maintenance") & filters.user(ADMINS))
async def maintenance_mode(client: Client, message: Message):
    global maintenance_mode_enabled
    
    if maintenance_mode_enabled:
        maintenance_mode_enabled = False
        await message.reply_text("Maintenance mode disabled.")
    else:
        maintenance_mode_enabled = True
        await message.reply_text("Maintenance mode enabled.")
        
@Client.on_message(filters.text & filters.user(ADMINS))
async def maintenance_mode_check(client: Client, message: Message):
    if maintenance_mode_enabled:
        await message.reply_text("Maintenance mode is enabled. Only admins can send messages.")
