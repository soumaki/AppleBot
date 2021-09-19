import os

from gtts import gTTS
from hachoir.metadata import extractMetadata as XMan
from hachoir.parser import createParser as CPR

from userge import Message, userge


@userge.on_cmd(
    "gv",
    about={
        "titulo": "Texto para áudio (idioma padrão é português)",
        "exemplos": ["{tr}gv (em resposta)", "{tr}gv -en Fuck off"],
    },
)
async def google_voz(message: Message):
    req_file_name = "gtts.mp3"
    reply = message.reply_to_message
    input_str = message.input_str
    def_lang = "pt"
    text = ""
    if input_str:
        input_str = input_str.strip()
        if reply:
            if (
                (reply.text or reply.caption)
                and len(input_str.split()) == 1
                and input_str.startswith("-")
            ):
                def_lang = input_str[1:]
                text = reply.text or reply.caption
        else:
            i_split = input_str.split(None, 1)
            if len(i_split) == 2 and i_split[0].startswith("-"):
                def_lang = i_split[0][1:]
                text = i_split[1]
            else:
                text = input_str
    elif reply and (reply.text or reply.caption):
        text = reply.text or reply.caption
    if not text:
        await message.err("Oshe!\nPreciso de um texto, né? Dã!", del_in=7)
        return
    try:
        await message.edit("Processando..")
        speeched = gTTS(text, lang=def_lang)
        speeched.save(req_file_name)
        meta = XMan(CPR(req_file_name))
        a_len = 0
        if meta and meta.has("duration"):
            a_len = meta.get("duration").seconds
        await message.edit("Gravando...")
        await message.client.send_voice(
            chat_id=message.chat.id,
            voice=req_file_name,
            duration=a_len,
            reply_to_message_id=reply.message_id if reply else None,
        )
        os.remove(req_file_name)
        await message.delete()
    except Exception as err:
        await message.err(str(err))
