import os
import PyPDF2
import time
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import User, Message, Document
from gtts import gTTS
from info import DOWNLOAD_LOCATION

Thanks = "That's The End Of Your Audio Book, And Thanks for Using this Service"

@Client.on_message(filters.command(["audiobook"]))
async def pdf_to_text(bot, message):
    try:
        if message.reply_to_message:
            pdf_path = DOWNLOAD_LOCATION + f"{message.chat.id}.pdf"
            txt = await message.reply("Downloading.....")
            await message.reply_to_message.download(pdf_path)
            await txt.edit("Downloaded File")
            
            pdf = open(pdf_path, 'rb')
            pdf_reader = PyPDF2.PdfFileReader(pdf)
            await txt.edit("Getting Number of Pages....")
            num_of_pages = pdf_reader.getNumPages()
            await txt.edit(f"Found {num_of_pages} Page")
            
            page_no = pdf_reader.getPage(0)
            await txt.edit("Finding Text from Pdf File... ")
            page_content = ""
            chat_id = message.chat.id
            with open(f'{message.chat.id}.txt', 'a+') as text_path:
                for page in range(0, num_of_pages):
                    page_no = pdf_reader.getPage(page)
                    page_content += page_no.extractText()
                    
            await txt.edit(f"Creating Your Audio Book...\n Please Don't Do Anything")
            output_text = page_content + Thanks
            
            language = 'en-in'
            tts_file = gTTS(text=output_text, lang=language, slow=False)
            tts_file.save(f"{message.chat.id}.mp3")
            
            with open(f"{message.chat.id}.mp3", "rb") as speech:
                await bot.send_voice(chat_id, speech)
            
            await txt.edit("𝚃𝙷𝙰𝙽𝙺𝚂 𝙵𝙾𝚁 𝚄𝚂𝙸𝙽𝙶 𝙼𝙴...☺️\n@iPepkornBots")
            os.remove(pdf_path)
        
        else:
            await message.reply("Please Reply to PDF file")
    
    except Exception as error:
        print(error)
        await txt.delete()
        os.remove(pdf_path)
