""" Manter os créditos | @applled - Baixar vídeos do YouTube"""

import random

from pyrogram.errors import BadRequest

from userge import Message, userge


@userge.on_cmd(
    "yt",
    about={
        "título": "MBaixar vídeos do YouTube",
        "exemplo": "{tr}yt https://youtu.be/dQw4w9WgXcQ",
    },
    del_pre=True,
    allow_channels=False,
)
async def appled_yt(message: Message):
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
        return await message.err("Lembre-se de fazer o comando + link", del_in=5)

    x = await userge.get_inline_bot_results("@youtubednbot", input_query)
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
            "Envie um link que seja do YouTube ou confira se ele existe.",
            del_in=5,
        )
