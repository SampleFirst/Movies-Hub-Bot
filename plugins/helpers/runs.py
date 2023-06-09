import random
from pyrogram import Client, filters, enums
from info import COMMAND_HAND_LER
from plugins.helper_functions.cust_p_filters import f_onw_fliter


RUN_STRINGS = (
    "A smooth sea never made a skilled sailor.",
    "A bird in the hand is worth two in the bush.",
    "When one door closes, another one opens.",
    "Actions speak louder than words.",
    "Don't count your chickens before they hatch.",
    "Every cloud has a silver lining.",
    "The early bird catches the worm.",
    "Where there's smoke, there's fire.",
    "You can't have your cake and eat it too.",
    "Don't judge a book by its cover.",
    "All that glitters is not gold.",
    "If the mountain won't come to Muhammad, Muhammad must go to the mountain.",
    "Better late than never.",
    "When in Rome, do as the Romans do.",
    "Two heads are better than one.",
    "The pen is mightier than the sword.",
    "The grass is always greener on the other side.",
    "Haste makes waste.",
    "A picture is worth a thousand words.",
    "Rome wasn't built in a day.",
)


@Client.on_message(
    filters.command("runs", COMMAND_HAND_LER) &
    f_onw_fliter
)
async def runs(_, message):
    """ /runs strings """
    effective_string = random.choice(RUN_STRINGS)
    if message.reply_to_message:
        await message.reply_to_message.reply_text(effective_string)
    else:
        await message.reply_text(effective_string)
