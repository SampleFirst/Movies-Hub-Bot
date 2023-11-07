from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait
from info import FILE_DB_CHANNEL
from database.ia_filterdb import Media, get_files_from_channel
import asyncio
import logging

MAX_BUTTON = 5

# Enable logging
logging.basicConfig(level=logging.INFO)


async def send_media_files_in_batches(bot, files, file_type, batch_size, chat_id, callback_query, batch_index=0):
    try:
        total_files = len(files)
        sent_count = 0
        corrupted_count = 0

        for i in range(batch_index, total_files, batch_size):
            batch = files[i:i + batch_size]
            for file in batch:
                try:
                    if file_type == "document":
                        await bot.send_document(chat_id=chat_id, document=file.file_id)
                    elif file_type == "video":
                        await bot.send_video(chat_id=chat_id, video=file.file_id)
                    elif file_type == "audio":
                        await bot.send_audio(chat_id=chat_id, audio=file.file_id)

                    sent_count += 1

                    # Update the message with live statistics
                    message = (
                        f"Total Files: {total_files}\n"
                        f"Sent Files: {sent_count}\n"
                        f"Corrupted Files: {corrupted_count}\n"
                        f"Batches Sent: {i // batch_size + 1}"
                    )

                    await callback_query.edit_message_text(message)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                except Exception as e:
                    corrupted_count += 1

            await asyncio.sleep(5)

        return total_files, sent_count, corrupted_count, i
    except Exception as e:
        return str(e)

@Client.on_message(filters.command("mystats"))
async def get_stats(_, message):
    try:
        total_documents = await Media.count_documents()
        total_videos = await Media.count_documents({"file_type": "video"})
        total_audio = await Media.count_documents({"file_type": "audio"})

        response_text = (
            f"Total Documents: {total_documents}\n"
            f"Total Videos: {total_videos}\n"
            f"Total Audio Files: {total_audio}"
        )

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Send Documents", callback_data="send_documents"),
                    InlineKeyboardButton("Send Videos", callback_data="send_videos"),
                ],
                [
                    InlineKeyboardButton("Send Audios", callback_data="send_audios"),
                    InlineKeyboardButton("Cancel Send", callback_data="cancel_send"),
                ],
            ]
        )

        await message.reply(response_text, reply_markup=keyboard)

    except Exception as e:
        logging.error(f"Error in get_stats: {str(e)}")

@Client.on_callback_query(filters.regex(r"send_documents"))
async def send_documents_button(bot, callback_query):
    try:
        files = await get_files_from_channel("document", MAX_BUTTON)
        if files:
            total_files, sent_count, corrupted_count, batch_index = await send_media_files_in_batches(
                bot, files, "document", MAX_BUTTON, FILE_DB_CHANNEL, callback_query
            )
            while sent_count < total_files:
                files = await get_files_from_channel("document", MAX_BUTTON, batch_index)
                total_files, sent_count, corrupted_count, batch_index = await send_media_files_in_batches(
                    bot, files, "document", MAX_BUTTON, FILE_DB_CHANNEL, callback_query, batch_index
                )
            message = (
                f"Total Documents: {total_files}\n"
                f"Sent Documents: {sent_count}\n"
                f"Corrupted Documents: {corrupted_count}\n"
                f"Batches Sent: {batch_index // MAX_BUTTON}"
            )
            await callback_query.message.reply_text(message)
        else:
            await callback_query.message.reply_text("No Documents found.")
    except Exception as e:
        logging.error(f"Error in send_documents_button: {str(e)}")

@Client.on_callback_query(filters.regex(r"send_videos"))
async def send_videos_button(bot, callback_query):
    try:
        files = await get_files_from_channel("video", MAX_BUTTON)
        if files:
            total_files, sent_count, corrupted_count, batch_index = await send_media_files_in_batches(
                bot, files, "video", MAX_BUTTON, FILE_DB_CHANNEL, callback_query
            )
            while sent_count < total_files:
                files = await get_files_from_channel("video", MAX_BUTTON, batch_index)
                total_files, sent_count, corrupted_count, batch_index = await send_media_files_in_batches(
                    bot, files, "video", MAX_BUTTON, FILE_DB_CHANNEL, callback_query, batch_index
                )
            message = (
                f"Total Videos: {total_files}\n"
                f"Sent Videos: {sent_count}\n"
                f"Corrupted Videos: {corrupted_count}\n"
                f"Batches Sent: {batch_index // MAX_BUTTON}"
            )
            await callback_query.message.reply_text(message)
        else:
            await callback_query.message.reply_text("No Videos found.")
    except Exception as e:
        logging.error(f"Error in send_videos_button: {str(e)}")

@Client.on_callback_query(filters.regex(r"send_audios"))
async def send_audios_button(bot, callback_query):
    try:
        files = await get_files_from_channel("audio", MAX_BUTTON)
        if files:
            total_files, sent_count, corrupted_count, batch_index = await send_media_files_in_batches(
                bot, files, "audio", MAX_BUTTON, FILE_DB_CHANNEL, callback_query
            )
            while sent_count < total_files:
                files = await get_files_from_channel("audio", MAX_BUTTON, batch_index)
                total_files, sent_count, corrupted_count, batch_index = await send_media_files_in_batches(
                    bot, files, "audio", MAX_BUTTON, FILE_DB_CHANNEL, callback_query, batch_index
                )
            message = (
                f"Total Audios: {total_files}\n"
                f"Sent Audios: {sent_count}\n"
                f"Corrupted Audios: {corrupted_count}\n"
                f"Batches Sent: {batch_index // MAX_BUTTON}"
            )
            await callback_query.message.reply_text(message)
        else:
            await callback_query.message.reply_text("No Audios found.")
    except Exception as e:
        logging.error(f"Error in send_audios_button: {str(e)}")

@Client.on_callback_query(filters.regex(r"cancel_send"))
async def cancel_send_button(bot, callback_query):
    try:
        await callback_query.edit_message_text("Canceling Send...")
        # Add your cancel logic here if needed
    except Exception as e:
        logging.error(f"Error in cancel_send_button: {str(e)}")

