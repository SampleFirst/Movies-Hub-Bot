from pyrogram import Client, filters
from info import DATABASE_NAME
from database.ia_filterdb import Media



@Client.on_message(filters.command("mystats"))
async def get_stats(_, message):
    total_documents = await Media.count_documents()
    total_videos = await Media.count_documents({"file_type": "video"})
    total_audio = await Media.count_documents({"file_type": "audio"})

    response_text = f"Total Documents: {total_documents}\nTotal Videos: {total_videos}\nTotal Audio Files: {total_audio}"

    await message.reply(response_text)
