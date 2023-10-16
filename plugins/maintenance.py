from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from info import ADMINS

maintenance_mode_enable = False

@Client.on_message(filters.command("maintenance") & filters.user(ADMINS))
async def maintenance_mode_command(client, message):
    global maintenance_mode_enable

    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("Mode", callback_data="maintenance_mode"),
            InlineKeyboardButton("False" if maintenance_mode_enable else "True", callback_data="maintenance_toggle")
        ]]
    )

    await message.reply_text("Maintenance mode options:", reply_markup=keyboard)


@Client.on_callback_query(filters.regex(r'^maintenance_toggle') & filters.user(ADMINS))
async def maintenance_toggle_callback(client, callback_query):
    global maintenance_mode_enable

    maintenance_mode_enable = not maintenance_mode_enable

    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("Mode", callback_data="maintenance_mode"),
            InlineKeyboardButton("False" if maintenance_mode_enable else "True", callback_data="maintenance_toggle")
        ]]
    )

    await callback_query.edit_message_reply_markup(reply_markup=keyboard)
    await callback_query.answer(f"Maintenance mode {'enabled' if maintenance_mode_enable else 'disabled'}")

@Client.on_message(filters.text & filters.command & filters.user(ADMINS))
async def maintenance_mode_check(client, message):
    if maintenance_mode_enable:
        await message.reply_text("♻️ Maintenance mode is enabled.")
        
