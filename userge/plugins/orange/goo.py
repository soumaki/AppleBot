"""Pesquisa simplificada do Google - @applled"""

import random
from userge import Config, Message, userge
from userge.utils import get_file_id, rand_array
from pyrogram import filters
import requests

from userge import Message, userge


@userge.on_cmd(
    "goo",
    about={
        "header": "Muito fácil usar o Google",
        "usar": "{tr}goo [pesquisar | responder]",
    },
)
async def goo_(message: Message):
    """ Google ;) """
    query = message.input_or_reply_str
    if not query:
        await message.edit("`Vou pesquisar o vento?!`")
        return
    query_encoded = query.replace(" ", "+")
    goo_url = f"https://www.google.com/search?q={query_encoded}"
    payload = {"format": "json", "url": goo_url}
    r = requests.get("http://is.gd/create.php", params=payload)
    texto = f"""{random.choice(RESULTADO)}"""
    photo = f"""{random.choice(ANIMTN)}"""
    await message.client.send_animation(
                         message.chat.id, 
                         animation=photo, 
                         caption=texto,
    )
#   await message.edit(
RESUTALDO = (
    f"""✅ **Este é o resultado da Sua Pesquisa no Google:\n\n🔗 [{query}]({r.json()['shorturl']})\n\n  ➖➖➖➖\nDev: @applled"""
    )

ANIMTN = (
    "https://telegra.ph/file/96378395294f719453c71.gif",
)
