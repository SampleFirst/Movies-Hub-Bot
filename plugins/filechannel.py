from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import Media, get_all_files
from info import ADMINS

@Client.on_message(filters.command("show_files") & filters.user(ADMINS))
async def show_files_command(client, message):
    try:
        page = 0  # Initialize the page offset
        max_results = 10  # Number of files to show per page

        # Get the list of files for the current page
        files, next_offset, total_results = await get_all_files(max_results, page * max_results)

        if not files:
            await message.reply("No files found.")
            return

        btn = [
            [
                InlineKeyboardButton(text=f"{file.file_name}", callback_data=f'send#{file.file_id}')
            ]
            for file in files
        ]

        if next_offset:
            btn.append(InlineKeyboardButton("Next", callback_data=f"next_{next_offset}"))
        if page > 0:
            btn.append(InlineKeyboardButton("Previous", callback_data=f"prev_{page - 1}"))

        cap = f"Here are the {total_results} media files found in the database."

        abc = await message.reply_text(cap, quote=True, reply_markup=InlineKeyboardMarkup(btn))

    except Exception as e:
        print(e)
        await message.reply("An error occurred while fetching files.")

@Client.on_callback_query(filters.regex(r"^(prev|next)_\d+"))
async def paginate_files(client, callback_query):
    data = callback_query.data.split("_")
    action, offset = data[0], int(data[1])

    max_results = 10

    if action == "prev" and offset > 0:
        page = offset - 1
    elif action == "next":
        page = offset

    files, next_offset, total_results = await get_all_files(max_results, page * max_results)

    if not files:
        await callback_query.answer("No more files.")
        return

    btn = [
        [
            InlineKeyboardButton(text=f"{file.file_name}", callback_data=f'send#{file.file_id}')
        ]
        for file in files
    ]

    if next_offset:
        btn.append(InlineKeyboardButton("Next", callback_data=f"next_{next_offset}"))
    if page > 0:
        btn.append(InlineKeyboardButton("Previous", callback_data=f"prev_{page - 1}"))

    await callback_query.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(btn)
    )
    await callback_query.answer()
    except Exception as e:
        # Handle any exceptions here
        print(f"An error occurred: {str(e)}")
