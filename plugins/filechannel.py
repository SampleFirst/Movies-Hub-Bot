import math
from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters
from database.ia_filterdb import Media, get_all_files, get_file_details
from info import ADMINS, MAX_BTTN, FILE_CHANNEL

max_results = MAX_BTTN
MAX_BTN = 10

def get_size(size):
    size = int(size)
    power = 2**10
    n = 0
    power_labels = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}

    while size > power:
        size /= power
        n += 1

    return f"{size:.2f} {power_labels[n]}"

    
@Client.on_message(filters.command("getallmedia") & filters.user(ADMINS))
async def send_all_media(client, message):
    try:
        files, offset, total_results = await get_all_files(max_results=max_results)

        btn = [
            [
                InlineKeyboardButton(text=f"{file.file_name}", callback_data=f'send#{file.file_id}')
            ]
            for file in files
        ]

        btn.insert(MAX_BTTN, 
            [
                InlineKeyboardButton("! Sᴇɴᴅ Aʟʟ !", callback_data=f"get_all")
            ]
        )
        if offset:
            page_number = int(offset) // max_results
            btn.append([
                InlineKeyboardButton(text=f"📄 Page {page_number}/{math.ceil(total_results / max_results)}", callback_data="pages"),
                InlineKeyboardButton(text="Next", callback_data=f"pmnext_{offset}")
            ])
        else:
            btn.append(
                [
                    InlineKeyboardButton(text=f"📄 Page 1/1", callback_data="pages")
                ]
            )

        cap = f"Here are the {total_results} media files found in the database."

        abc = await message.reply_text(cap, quote=True, reply_markup=InlineKeyboardMarkup(btn))
    except Exception as e:
        # Handle any exceptions here
        print(f"An error occurred: {str(e)}")
        
@Client.on_callback_query(filters.regex(r'^pmnext_'))
async def next_page_button(client, query: CallbackQuery):
    try:
        offset = query.data.split("_")[1]
        files, new_offset, total_results = await get_all_files(max_results=max_results, offset=int(offset))
        page_number = int(offset) // max_results + 1

        btn = [
            [InlineKeyboardButton(text=f"{file.file_name}", callback_data=f'send#{file.file_id}')]
            for file in files
        ]
        btn.insert(MAX_BTTN,
         [
            InlineKeyboardButton("! Sᴇɴᴅ Aʟʟ !", callback_data=f"get_all")
        ])
        if new_offset:
            page_number = int(new_offset) // max_results + 1
            prev_offset = int(offset) - max_results  # Calculate the previous page offset
            if prev_offset >= 0:
                btn.append([
                    InlineKeyboardButton(text="Previous", callback_data=f"pmprev_{prev_offset}"),
                    InlineKeyboardButton(text=f"📄 Page {page_number}/{math.ceil(total_results / max_results)}", callback_data="pages"),
                    InlineKeyboardButton(text="Next", callback_data=f"pmnext_{new_offset}")
                ])
            else:
                btn.append([
                    InlineKeyboardButton(text=f"📄 Page {page_number}/{math.ceil(total_results / max_results)}", callback_data="pages"),
                    InlineKeyboardButton(text="Next", callback_data=f"pmnext_{new_offset}")
                ])
        else:
            btn.append([InlineKeyboardButton(text=f"📄 Page {page_number}/{math.ceil(total_results / max_results)}", callback_data="pages")])

        await query.edit_message_text(
            text=query.message.text.markdown,
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except Exception as e:
        # Handle any exceptions here
        print(f"An error occurred: {str(e)}")

@Client.on_callback_query(filters.regex(r'^pmprev_'))
async def prev_page_button(client, query: CallbackQuery):
    try:
        offset = query.data.split("_")[1]
        files, new_offset, total_results = await get_all_files(max_results=max_results, offset=int(offset))
        page_number = int(offset) // max_results + 1

        btn = [
            [InlineKeyboardButton(text=f"{file.file_name}", callback_data=f'send#{file.file_id}')]
            for file in files
        ]
        btn.insert(MAX_BTTN,
         [
            InlineKeyboardButton("! Sᴇɴᴅ Aʟʟ !", callback_data=f"get_all")
        ])
        if new_offset:
            page_number = int(new_offset) // max_results + 1
            prev_offset = int(offset) - max_results
            next_offset = int(offset) + max_results

            if prev_offset >= 0:
                btn.append([
                    InlineKeyboardButton(text="Previous", callback_data=f"pmprev_{prev_offset}"),
                    InlineKeyboardButton(text=f"📄 Page {page_number}/{math.ceil(total_results / max_results)}", callback_data="pages"),
                ])
            if next_offset < total_results:
                btn.append([
                    InlineKeyboardButton(text=f"📄 Page {page_number}/{math.ceil(total_results / max_results)}", callback_data="pages"),
                    InlineKeyboardButton(text="Next", callback_data=f"pmnext_{next_offset}")
                ])
                await query.edit_message_text(
                    text=query.message.text.markdown,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
        else:
            btn.append([InlineKeyboardButton(text=f"📄 Page {page_number}/{math.ceil(total_results / max_results)}", callback_data="pages")])

        await query.edit_message_text(
            text=query.message.text.markdown,
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except Exception as e:
        # Handle any exceptions here
        print(f"An error occurred: {str(e)}")


@Client.on_callback_query(filters.regex(r'^send#'))
async def send_media_to_channel(client, query: CallbackQuery):
    try:
        file_id = query.data.split("#")[1]
        files_ = await get_file_details(file_id)
        
        if not files_:
            return await query.answer('No such file exists.')
        
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        
        # Send the selected media to the FILE_CHANNEL
        await client.send_cached_media(
            chat_id=FILE_CHANNEL,
            file_id=file_id,
            caption=title,
        )
        
        await query.answer('Media sent to the channel.')
    except Exception as e:
        # Handle any exceptions here
        print(f"An error occurred: {str(e)}")

@Client.on_callback_query(filters.regex(r'^get_all'))
async def send_all_media_to_channel(client, query: CallbackQuery):
    try:
        files, offset, total_results = await get_all_files(max_results=max_results)

        file_list = []
        total_size = 0

        for file in files:
            file_list.append(f"{file.file_name} - {get_size(file.file_size)}")
            total_size += file.file_size

            await client.send_media(FILE_CHANNEL, file.file_id)
        
        file_list.append(f"Total: {get_size(total_size)}")

        # Save the list of sent files to a .txt file
        with open("sent_files.txt", "w") as file_txt:
            for line in file_list:
                file_txt.write(f"{line}\n")

        # Send the .txt file as a document
        await client.send_document(FILE_CHANNEL, document="sent_files.txt")

        await query.answer("All media sent to the channel. File list sent as a .txt document.")
    except Exception as e:
        # Handle any exceptions here
        print(f"An error occurred: {str(e)}")

