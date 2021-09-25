""" Plugin para baixar vídeos do YouTube / @applled """

from pyrogram.errors import BadRequest

from userge import Message, userge
from userge.utils import get_file_id


@userge.on_cmd(
    "yt",
    about={
        "titulo": "Baixe vídeos do Youtube",
        "como usar": ".yt + link de um vídeo",
    },
)
async def yt_link_at_applled(message: Message):
    """Plugin para baixar vídeos do YouTube / @applled"""
    youtube = message.input_str
    if not youtube:
        await message.err(
            "Envie um link que seja do YouTube ou confira se ele existe.", del_in=10
        )
        return
    search = await message.edit(
        "Confira o resultado em: @youtubednbot\nSolicitação de Download: **{}**".format(
            youtube
        )
    )
    chat_id = message.chat.id
    f_id = ""
    try:
        async for msg in userge.search_messages(
            "@youtubednbot", query=youtube, limit=1, filter="document"
        ):
            f_id = get_file_id(msg)
    except BadRequest:
        await search.edit("Obrigatório que seja um link de um vídeo no YouTube.")
        return
    if not f_id:
        await search.edit("**Falha na Matrix:** Não encontrei foi nada...", del_in=5)
        return
    await userge.send_document(chat_id, f_id)
    await search.delete()
