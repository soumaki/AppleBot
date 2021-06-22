""" kang stickers """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import io
import os
import random

from bs4 import BeautifulSoup as bs
from PIL import Image
from pyrogram import emoji
from pyrogram.errors import StickersetInvalid, YouBlockedUser
from pyrogram.raw.functions.messages import GetStickerSet
from pyrogram.raw.types import InputStickerSetShortName

from userge import Config, Message, userge
from userge.utils import get_response


@userge.on_cmd(
    "kibar",
    about={
        "header": "Kiba adesivos ou cria um",
        "flags": {"-s": "without link", "-d": "without trace"},
        "como usar": "Responda {tr}kibar [emoji('s)] [número do pack] para criar um adesivo ou "
        "uma imagem para kibar.",
        "exemplos": [
            "{tr}kibar",
            "{tr}kibar -s",
            "{tr}kibar -d",
            "{tr}kibar 🤔",
            "{tr}kibar 2",
            "{tr}kibar 🤔 2",
        ],
    },
    allow_channels=False,
    allow_via_bot=False,
)
async def kang_(message: Message):
    """Kibar um adesivo"""
    user = await userge.get_me()
    replied = message.reply_to_message
    photo = None
    emoji_ = None
    is_anim = False
    resize = False
    if replied and replied.media:
        if replied.photo:
            resize = True
        elif replied.document and "image" in replied.document.mime_type:
            resize = True
        elif replied.document and "tgsticker" in replied.document.mime_type:
            is_anim = True
        elif replied.sticker:
            if not replied.sticker.file_name:
                await message.edit("`Adeviso nem nome tem!`")
                return
            emoji_ = replied.sticker.emoji
            is_anim = replied.sticker.is_animated
            if not replied.sticker.file_name.endswith(".tgs"):
                resize = True
        else:
            await message.edit("`Este tipo de arquivo não é suportado!`")
            return
        await message.edit(f"`{random.choice(KANGING_STR)}`")
        photo = await userge.download_media(message=replied, file_name=Config.DOWN_PATH)
    else:
        await message.edit("`Puts, impossível kibar isso...`")
        return
    if photo:
        args = message.filtered_input_str.split()
        pack = 1
        if len(args) == 2:
            emoji_, pack = args
        elif len(args) == 1:
            if args[0].isnumeric():
                pack = int(args[0])
            else:
                emoji_ = args[0]

        if emoji_ and emoji_ not in (
            getattr(emoji, _) for _ in dir(emoji) if not _.startswith("_")
        ):
            emoji_ = None
        if not emoji_:
            emoji_ = "🤔"

        u_name = user.username
        u_name = "@" + u_name if u_name else user.first_name or user.id
        packname = f"a{user.id}_by_x_{pack}"
        custom_packnick = Config.CUSTOM_PACK_NAME or f"{u_name}' - Pacote Premium"
        packnick = f"{custom_packnick} Vol.{pack}"
        cmd = "/newpack"
        if resize:
            photo = resize_photo(photo)
        if is_anim:
            packname += "_anim"
            packnick += " (Animated)"
            cmd = "/newanimated"
        exist = False
        try:
            exist = await message.client.send(
                GetStickerSet(stickerset=InputStickerSetShortName(short_name=packname))
            )
        except StickersetInvalid:
            pass
        if exist is not False:
            async with userge.conversation("Stickers", limit=30) as conv:
                try:
                    await conv.send_message("/addsticker")
                except YouBlockedUser:
                    await message.edit("first **unblock** @Stickers")
                    return
                await conv.get_response(mark_read=True)
                await conv.send_message(packname)
                msg = await conv.get_response(mark_read=True)
                limit = "50" if is_anim else "120"
                while limit in msg.text:
                    pack += 1
                    packname = f"a{user.id}_by_userge_{pack}"
                    packnick = f"{custom_packnick} Vol.{pack}"
                    if is_anim:
                        packname += "_anim"
                        packnick += " (Animated)"
                    await message.edit(
                        "`Mudando para o Pack "
                        + str(pack)
                        + " devido a falta de espaço`"
                    )
                    await conv.send_message(packname)
                    msg = await conv.get_response(mark_read=True)
                    if msg.text == "Esse pacote selecionado deve nem existir.":
                        await conv.send_message(cmd)
                        await conv.get_response(mark_read=True)
                        await conv.send_message(packnick)
                        await conv.get_response(mark_read=True)
                        await conv.send_document(photo)
                        await conv.get_response(mark_read=True)
                        await conv.send_message(emoji_)
                        await conv.get_response(mark_read=True)
                        await conv.send_message("/publish")
                        if is_anim:
                            await conv.get_response(mark_read=True)
                            await conv.send_message(f"<{packnick}>", parse_mode=None)
                        await conv.get_response(mark_read=True)
                        await conv.send_message("/skip")
                        await conv.get_response(mark_read=True)
                        await conv.send_message(packname)
                        await conv.get_response(mark_read=True)
                        if "-d" in message.flags:
                            await message.delete()
                        else:
                            out = (
                                "__kanged__"
                                if "-s" in message.flags
                                else f"[kanged](t.me/addstickers/{packname})"
                            )
                            await message.edit(
                                f"**Adeviso** {out} __está em um pacote diferente__**!**"
                            )
                        return
                await conv.send_document(photo)
                rsp = await conv.get_response(mark_read=True)
                if "Foi mal, este tipo de arquivo é um lixo." in rsp.text:
                    await message.edit(
                        "`Falha ao adicionar, use` @Stickers "
                        "`bot para adicionar o adesivo manualmente.`"
                    )
                    return
                await conv.send_message(emoji_)
                await conv.get_response(mark_read=True)
                await conv.send_message("/done")
                await conv.get_response(mark_read=True)
        else:
            await message.edit("`Criando um novo pacote...`")
            async with userge.conversation("Stickers") as conv:
                try:
                    await conv.send_message(cmd)
                except YouBlockedUser:
                    await message.edit("Primeiramente, **desbloqueie** o @Stickers")
                    return
                await conv.get_response(mark_read=True)
                await conv.send_message(packnick)
                await conv.get_response(mark_read=True)
                await conv.send_document(photo)
                rsp = await conv.get_response(mark_read=True)
                if "Foi mal, este tipo de arquivo é um lixo." in rsp.text:
                    await message.edit(
                        "`Falha ao adicionar, use` @Stickers "
                        "`bot para adicionar o adesivo manualmente.`"
                    )
                    return
                await conv.send_message(emoji_)
                await conv.get_response(mark_read=True)
                await conv.send_message("/publish")
                if is_anim:
                    await conv.get_response(mark_read=True)
                    await conv.send_message(f"<{packnick}>", parse_mode=None)
                await conv.get_response(mark_read=True)
                await conv.send_message("/skip")
                await conv.get_response(mark_read=True)
                await conv.send_message(packname)
                await conv.get_response(mark_read=True)
        if "-d" in message.flags:
            await message.delete()
        else:
            out = (
                "__kibado__"
                if "-s" in message.flags
                else f"[kibado](t.me/addstickers/{packname})"
            )
            await message.edit(f"**Adesivo** {out}**!**")
        if os.path.exists(str(photo)):
            os.remove(photo)


@userge.on_cmd(
    "kibinfo",
    about={
        "header": "Obtenha informações do pacote de adesivo",
        "como usar": "responda {tr}kibinfo em qualquer adeviso",
    },
)
async def sticker_pack_info_(message: Message):
    """Obtenha informações do pacote"""
    replied = message.reply_to_message
    if not replied:
        await message.edit("`Não consegui identificar essa desgraça, ou eu posso?!`")
        return
    if not replied.sticker:
        await message.edit(
            "`Responda a um adesivo para obter informações detalhadas do pacote`"
        )
        return
    await message.edit("`Buscando informações do pacote de adesivos, pera aí..`")
    get_stickerset = await message.client.send(
        GetStickerSet(
            stickerset=InputStickerSetShortName(short_name=replied.sticker.set_name)
        )
    )
    pack_emojis = []
    for document_sticker in get_stickerset.packs:
        if document_sticker.emoticon not in pack_emojis:
            pack_emojis.append(document_sticker.emoticon)
    out_str = (
        f"**Título do Adesivo:** `{get_stickerset.set.title}\n`"
        f"**Nome Curto:** `{get_stickerset.set.short_name}`\n"
        f"**Arquivado:** `{get_stickerset.set.archived}`\n"
        f"**Oficial:** `{get_stickerset.set.official}`\n"
        f"**Máscaras:** `{get_stickerset.set.masks}`\n"
        f"**Animados:** `{get_stickerset.set.animated}`\n"
        f"**Adesivos no Pacote:** `{get_stickerset.set.count}`\n"
        f"**Emojis no Pacote:**\n{' '.join(pack_emojis)}"
    )
    await message.edit(out_str)


def resize_photo(photo: str) -> io.BytesIO:
    """Redimensiona a imagem para 512x512"""
    image = Image.open(photo)
    maxsize = 512
    scale = maxsize / max(image.width, image.height)
    new_size = (int(image.width * scale), int(image.height * scale))
    image = image.resize(new_size, Image.LANCZOS)
    resized_photo = io.BytesIO()
    resized_photo.name = "sticker.png"
    image.save(resized_photo, "PNG")
    os.remove(photo)
    return resized_photo


KANGING_STR = (
    "Vamos lá, hora de kibar...",
    "Estou sim, kibando essa desgraça de adesivo...",
    "Kibando, vai me processar?",
    "KIBAANNNDDOOOO...",
    "Seria uma pena se alguém kibasse isso, né?",
)


# Baseado em:
# https://github.com/AnimeKaizoku/SaitamaRobot/blob/10291ba0fc27f920e00f49bc61fcd52af0808e14/SaitamaRobot/modules/stickers.py#L42
@userge.on_cmd(
    "adesivo",
    about={
        "header": "Pesquise por pacotes de Adesivos",
        "como usar": "Responda {tr}adesivo ou " "{tr}adesivo [texto]",
    },
)
async def sticker_search(message: Message):
    # search sticker packs
    reply = message.reply_to_message
    query_ = None
    if message.input_str:
        query_ = message.input_str
    elif reply and reply.from_user:
        query_ = reply.from_user.username or reply.from_user.id

    if not query_:
        return message.err(
            "responda uma mensagem ou forneça um texto para a pesquisa do pacote",
            del_in=3,
        )

    await message.edit(f'🔎 Pesquisando por "`{query_}`"...')
    titlex = f'<b>Pacotes de Adesivos:</b> "<u>{query_}</u>"\n'
    sticker_pack = ""
    try:
        text = await get_response.text(
            f"https://combot.org/telegram/stickers?q={query_}"
        )
    except ValueError:
        return await message.err(
            "API com problemas, o bot quase morreu.\n Tente de novo.",
            del_in=5,
        )
    soup = bs(text, "lxml")
    results = soup.find_all("div", {"class": "sticker-pack__header"})
    for pack in results:
        if pack.button:
            title_ = (pack.find("div", {"class": "sticker-pack__title"})).text
            link_ = (pack.a).get("href")
            sticker_pack += f"\n• [{title_}]({link_})"
    if not sticker_pack:
        sticker_pack = "`❌ Não encontrei foi nada!`"
    await message.edit((titlex + sticker_pack), disable_web_page_preview=True)
