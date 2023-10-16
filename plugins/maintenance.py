from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS

maintenance_mode_enabled = False

@Client.on_message(filters.command("maintenance") & filters.user(ADMINS))
async def maintenance_mode(client, message):
    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("Mode", callback_data="maintenance_mode"),
            InlineKeyboardButton("OFF" if maintenance_mode_enabled else "ON", callback_data="maintenance_toggle")
        ]]
    )

    await message.reply_text("Maintenance mode options:", reply_markup=keyboard, quote=True)


@Client.on_callback_query(filters.regex(r'^maintenance_toggle') & filters.user(ADMINS))
async def maintenance_toggle(client, callback_query):
    global maintenance_mode_enabled
    maintenance_mode_enabled = not maintenance_mode_enabled

    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("Mode", callback_data="maintenance_mode"),
            InlineKeyboardButton("OFF" if maintenance_mode_enabled else "ON", callback_data="maintenance_toggle")
        ]]
    )

    await callback_query.edit_message_reply_markup(reply_markup=keyboard)
    await callback_query.answer("Maintenance mode is " + ("OFF" if maintenance_mode_enabled else "ON"), show_alert=True)


@Client.on_message(filters.text & filters.incoming)
async def maintenance_mode_handler(client, message):
    global maintenance_mode_enabled
    user_id = message.from_user.id

    if maintenance_mode_enabled and user_id not in ADMINS:
        await message.reply_text("♻️ Maintenance mode is enabled.", quote=True)
    
    
