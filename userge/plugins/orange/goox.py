""" Manter os créditos | @applled - Módulo que gera um adesivo animado de pesquisa do Google"""

from pyrogram.errors import BadRequest

from userge import Message, userge


@userge.on_cmd(
    "gx",
    about={
        "header": "Módulo criado pelo @applled que gera um adesivo animado de pesquisa do Google",
        "como usar": "{tr}gx amo maçãs",
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
        return await message.err(
            "Lembre-se de fazer o comando + texto de pesquisa", del_in=5
        )

    x = await userge.get_inline_bot_results("@GooglaxBot", input_query)
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
            "Não é assim que funciona, jovem...",
            del_in=5,
        )
