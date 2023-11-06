from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import MAX_BTN, FILE_DB_CHANNEL 
from database.ia_filterdb import Media, get_files_from_channel
import time

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

async def send_media_files(chat_id, files, file_type, callback_query):
    try:
        batches = [files[i:i + MAX_BTN] for i in range(0, len(files), MAX_BTN)]
        for batch in batches:
            if file_type == "document":
                for file in batch:
                    await bot.send_document(
                        chat_id=chat_id,
                        document=file.file_id,
                    )
                await callback_query.answer(f"Sent {len(batch)} Documents")
            elif file_type == "video":
                for file in batch:
                    await bot.send_video(
                        chat_id=chat_id,
                        video=file.file_id,
                    )
                await callback_query.answer(f"Sent {len(batch)} Videos")
            elif file_type == "audio":
                for file in batch:
                    await bot.send_audio(
                        chat_id=chat_id,
                        audio=file.file_id,
                    )
                await callback_query.answer(f"Sent {len(batch)} Audios")
            time.sleep(2)  # Introduce a 2-second break between batches
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}")

@Client.on_callback_query(filters.regex(r"send_documents"))
async def send_documents_button(bot, callback_query):
    files = await get_files_from_channel("document", MAX_BTN)
    if files:
        await send_media_files(FILE_DB_CHANNEL, files, "document", callback_query)
    else:
        await callback_query.answer("No Documents found.")

@Client.on_callback_query(filters.regex(r"send_videos"))
async def send_videos_button(bot, callback_query):
    files = await get_files_from_channel("video", MAX_BTN)
    if files:
        await send_media_files(FILE_DB_CHANNEL, files, "video", callback_query)
    else:
        await callback_query.answer("No Videos found.")

@Client.on_callback_query(filters.regex(r"send_audios"))
async def send_audios_button(bot, callback_query):
    files = await get_files_from_channel("audio", MAX_BTN)
    if files:
        await send_media_files(FILE_DB_CHANNEL, files, "audio", callback_query)
    else:
        await callback_query.answer("No Audios found.")

@Client.on_callback_query(filters.regex(r"cancel_send"))
async def cancel_send_button(bot, callback_query):
    await callback_query.answer("Canceling Send...")
