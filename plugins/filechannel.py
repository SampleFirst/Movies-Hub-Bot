from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import get_search_results, Media, get_file_details

# Define a command handler function
@Client.on_message(filters.command("show_files") & filters.user(ADMINS))
async def show_files_command(client, message):
    # Extract chat ID
    chat_id = message.chat.id

    # Get the user's query from the message
    query = message.text.split(maxsplit=1)
    if len(query) > 1:
        query = query[1].strip()
    else:
        query = ""

    # Define a function to generate inline keyboard buttons for pagination
    def generate_pagination_buttons(offset, total_results):
        buttons = []

        if offset > 0:
            buttons.append(
                InlineKeyboardButton(
                    "PREVIOUS",
                    callback_data=f"prev_{offset - 10}_{total_results}",
                )
            )

        if offset + 10 < total_results:
            buttons.append(
                InlineKeyboardButton(
                    "NEXT",
                    callback_data=f"next_{offset + 10}_{total_results}",
                )
            )

        return buttons

    # Get search results
    files, next_offset, total_results = await get_search_results(chat_id, query, max_results=10)

    # Create a list of file names for displaying in the message
    file_names = [file.file_name for file in files]

    # Create an inline keyboard for pagination
    pagination_buttons = generate_pagination_buttons(0, total_results)

    # Create a message with the list of files and pagination buttons
    if file_names:
        message_text = "\n".join(file_names)
        reply_markup = InlineKeyboardMarkup([pagination_buttons])
    else:
        message_text = "No files found."
        reply_markup = None

    # Send the message with the inline keyboard
    await message.reply_text(message_text, reply_markup=reply_markup)

