from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import DATABASE_NAME, FILE_CHANNEL
from database.ia_filterdb import Media

@Client.on_message(filters.command("mystats"))
async def get_stats(_, message):
    total_documents = await Media.count_documents()
    total_videos = await Media.count_documents({"file_type": "video"})
    total_audio = await Media.count_documents({"file_type": "audio"})

    response_text = f"Total Documents: {total_documents}\nTotal Videos: {total_videos}\nTotal Audio Files: {total_audio}"

    # Create inline keyboard with 4 buttons
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Send Documents", callback_data="send_documents"),
                InlineKeyboardButton("Send Videos", callback_data="send_videos")
            ],
            [
                InlineKeyboardButton("Send Audios", callback_data="send_audios"),
                InlineKeyboardButton("Cancel Send", callback_data="cancel_send")
            ],
        ]
    )

    await message.reply(
        response_text,
        reply_markup=keyboard,
    )
