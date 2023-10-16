from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS

maintenance_mode = False

@Client.on_message(filters.command("maintenance") & filters.user(ADMINS))
async def maintenance_mode_command(client, message):
    global maintenance_mode

    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("Mode", callback_data="maintenance_mode"),
            InlineKeyboardButton("OFF" if maintenance_mode else "ON", callback_data="maintenance_toggle")
        ]]
    )

    await message.reply_text("Maintenance mode options:", reply_markup=keyboard)


@Client.on_callback_query(filters.regex(r'^maintenance_toggle') & filters.user(ADMINS))
async def maintenance_toggle_callback(client, callback_query):
    global maintenance_mode

    maintenance_mode = not maintenance_mode

    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("Mode", callback_data="maintenance_mode"),
            InlineKeyboardButton("OFF" if maintenance_mode else "ON", callback_data="maintenance_toggle")
        ]]
    )

    await callback_query.edit_message_reply_markup(reply_markup=keyboard)
    await callback_query.answer(f"Maintenance mode {'enabled' if maintenance_mode else 'disabled'}")


@Client.on_message(filters.text & filters.command)
async def maintenance_mode_check(client, message):
    user_id = message.from_user.id

    if maintenance_mode and user_id not in ADMINS:
        await message.reply_text("♻️ Maintenance mode is enabled.")
    else:
        # Your regular processing code here
        pass
