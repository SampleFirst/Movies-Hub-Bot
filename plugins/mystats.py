from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import MAX_BTN
from database.ia_filterdb import Media, get_files_from_channel

@Client.on_message(filters.command("mystats"))
async def get_stats(_, message):
    total_documents = await Media.count_documents()
    total_videos = await Media.count_documents({"file_type": "video"})
    total_audio = await Media.count_documents({"file_type": "audio"})

    response_text = f"Total Documents: {total_documents}\nTotal Videos: {total_videos}\nTotal Audio Files: {total_audio}"

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

@Client.on_callback_query(filters.regex(r"send_documents"))
async def send_documents_button(_, callback_query):
    try:
        files = await get_files_from_channel("document", MAX_BTN)
        if files:
            for file in files:
                await callback_query.message.reply_document(file.file_id)
            await callback_query.answer(f"Sent {len(files)} Documents")
        else:
            await callback_query.answer("No Documents found.")
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}")

@Client.on_callback_query(filters.regex(r"send_videos"))
async def send_videos_button(_, callback_query):
    try:
        files = await get_files_from_channel("video", MAX_BTN)
        if files:
            for file in files:
                await callback_query.message.reply_video(file.file_id)
            await callback_query.answer(f"Sent {len(files)} Videos")
        else:
            await callback_query.answer("No Videos found.")
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}")

@Client.on_callback_query(filters.regex(r"send_audios"))
async def send_audios_button(_, callback_query):
    try:
        files = await get_files_from_channel("audio", MAX_BTN)
        if files:
            for file in files:
                await callback_query.message.reply_audio(file.file_id)
            await callback_query.answer(f"Sent {len(files)} Audios")
        else:
            await callback_query.answer("No Audios found.")
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}")

@Client.on_callback_query(filters.regex(r"cancel_send"))
async def cancel_send_button(_, callback_query):
    await callback_query.answer("Canceling Send...")

    
