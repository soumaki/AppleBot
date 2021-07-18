import os

from telegraph import upload_file

from userge import Config, Message, userge
from userge.utils import progress

_T_LIMIT = 5242880


@userge.on_cmd(
    "teleg",
    about={
        "header": "Faça o upload de algum arquivo para os servidores do Telegraph",
        "formatos": [".jpg", ".jpeg", ".png", ".gif", ".mp4"],
        "como usar": "responda {tr}teleg para um arquivo suportado : o limite é de 5MB",
    },
)
async def telegraph_(message: Message):
    replied = message.reply_to_message
    if not replied:
        await message.err(
            "Oh, responda uma mensagem que contenha um arquivo que seja suportado."
        )
        return
    link = await upload_media_(message)
    if not link:
        return
    await message.edit(
        f"**Tudo certo, este é o [link](https://telegra.ph{link})\nSe preferir:\n <code>{link}</code>**",
        disable_web_page_preview=True,
    )


async def upload_media_(message: Message):
    replied = message.reply_to_message
    if not (
        (replied.photo and replied.photo.file_size <= _T_LIMIT)
        or (replied.animation and replied.animation.file_size <= _T_LIMIT)
        or (
            replied.video
            and replied.video.file_name.endswith((".mp4", ".mkv"))
            and replied.video.file_size <= _T_LIMIT
        )
        or (
            replied.document
            and replied.document.file_name.endswith(
                (".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mkv")
            )
            and replied.document.file_size <= _T_LIMIT
        )
    ):
        await message.err("Este tipo de arquivo não é suportado, foi mal...")
        return
    await message.edit("`Enviando para o servidor...`")
    dl_loc = await message.client.download_media(
        message=message.reply_to_message,
        file_name=Config.DOWN_PATH,
        progress=progress,
        progress_args=(message, "Solicitando o Download"),
    )
    await message.edit("`Enviando para o Telegraph...`")
    try:
        response = upload_file(dl_loc)
    except Exception as t_e:
        await message.err(t_e)
        return
    os.remove(dl_loc)
    return str(response[0])
