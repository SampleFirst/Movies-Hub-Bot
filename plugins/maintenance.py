from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS

maintenance_mode_enabled = False

@Client.on_message(filters.command("maintenance") & filters.user(ADMINS))
async def maintenance_mode(client: Client, message: Message):
    global maintenance_mode_enabled

    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("Mode", callback_data="maintenance_mode"),
            InlineKeyboardButton("OFF" if maintenance_mode_enabled else "ON", callback_data="maintenance_toggle")
        ]]
    )

    if maintenance_mode_enabled:
        maintenance_mode_enabled = False
        await message.reply_text("Maintenance mode disabled.", reply_markup=keyboard)
    else:
        maintenance_mode_enabled = True
        await message.reply_text("Maintenance mode enabled.", reply_markup=keyboard)


@Client.on_callback_query(filters.regex(r'^maintenance_toggle') & filters.user(ADMINS))
async def maintenance_toggle(client, message):
    global maintenance_mode_enabled

    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("Mode", callback_data="maintenance_mode"),
            InlineKeyboardButton("OFF" if maintenance_mode_enabled else "ON", callback_data="maintenance_toggle")
        ]]
    )

    if maintenance_mode_enabled:
        maintenance_mode_enabled = False
        await message.reply_text("Maintenance mode disabled.", reply_markup=keyboard)
    else:
        maintenance_mode_enabled = True
        await message.reply_text("Maintenance mode enabled.", reply_markup=keyboard)


@Client.on_callback_query(filters.regex(r'^maintenance_mode'))
async def maintenance_mode_info(client, message):
    await message.answer_text(f"Select maintenance mode: {'ON' if maintenance_mode_enabled else 'OFF'}", show_alert=True)


@Client.on_message(filters.text & filters.command)
async def maintenance_mode_check(client, message):
    user_id = message.from_user.id

    if maintenance_mode_enabled and user_id not in ADMINS:
        await message.reply_text("♻️ Maintenance mode is enabled.")
    else:
        # Your regular processing code here
        pass

                   
