""" Manter os créditos | @applled - Módulo que exibe qual música você está ouvindo no Spotify"""

import random

from pyrogram.errors import BadRequest

from userge import Message, userge

NOW = ("sp",)
COMANDO = ("now",)


@userge.on_cmd(
    "sp",
    about={
        "header": "Módulo criado pelo @applled que exibe qual música você está ouvindo no Spotify",
        "como usar": "{tr}sp /now",
    },
    del_pre=True,
    allow_channels=False,
)
async def appled_(message: Message):
    reply = message.reply_to_message
    reply_id = reply.message_id if reply else None
    if message.input_str:
        input_query = message.input_str
    elif reply:
        if reply.text:
            input_query = reply.text
        elif reply.caption:
            input_query = reply.caption
    if not input_query:
        return await message.err("Lembre-se de fazer o comando + /now", del_in=5)

    x = await userge.get_inline_bot_results("@spotipiebot", input_query)
    try:
        await message.delete()
        await userge.send_inline_bot_result(
            chat_id=message.chat.id,
            query_id=x.query_id,
            result_id=x.results[0].id,
            reply_to_message_id=reply_id,
            hide_via=True,
        )
    except (IndexError, BadRequest):
        await message.err(
            "Você realmente está ouvindo algo no Spotify?\nConfira se você ao menos iniciou a música.",
            del_in=5,
        )


# COMANDO COM O BOT


@userge.on_cmd(
    "apple$",
    about={
        "título": "Comando rápido para o Now Playing / Comando usado somente quando seu bot estiver no mesmo grupo e como administrador."
    },
    trigger="",
    allow_via_bot=False,
)
async def ouvindo_(message: Message):
    await message.edit(
        "!sp /now",
        del_in=1,
    )


@userge.on_cmd(
    "spf",
    about={
        "título": "@applled",
        "como usar": "{tr}spf",
    },
    del_pre=True,
    allow_channels=False,
)
async def conectar(message: Message):
    """Ação rápida"""
    await message.edit("`Conectado ao Spotify ✅`", log=__name__)
    #   if "n" in message.flags:
    await message.edit(
        f",{random.choice(NOW)} /{random.choice(COMANDO)}",
        del_in=2,
    )
    await message.edit(f".sp /no")
