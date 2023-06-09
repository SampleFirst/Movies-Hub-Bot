import time
import random
from pyrogram import Client, filters
from info import COMMAND_HAND_LER
from plugins.helper_functions.cust_p_filters import f_onw_fliter


ALIVE = "<b>I'm alive and kicking! You're still here, right? Seems like you don't have any affection towards me. It's fine... You can try /start to see if something changes...🙂</b>"


@Client.on_message(filters.command("alive", COMMAND_HAND_LER) & f_onw_fliter)
async def check_alive(_, message):
    await message.reply_text(ALIVE)


@Client.on_message(filters.command("ping", COMMAND_HAND_LER) & f_onw_fliter)
async def ping(_, message):
    start_t = time.time()
    rm = await message.reply_text("...")
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await rm.edit(f"<b>Pong!\n{time_taken_s:.3f} ms\n\n@iPepkornBots</b>")






