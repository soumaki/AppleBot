""" Configurações para PM """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
from typing import Dict

from userge import Config, Message, filters, get_collection, userge
from userge.utils import SafeDict
from userge.utils.extras import reported_user_image

CHANNEL = userge.getCLogger(__name__)
SAVED_SETTINGS = get_collection("CONFIGS")
ALLOWED_COLLECTION = get_collection("PM_PERMIT")
PMPERMIT_MSG = {}


pmCounter: Dict[int, int] = {}
allowAllFilter = filters.create(lambda _, __, ___: Config.ALLOW_ALL_PMS)
noPmMessage = bk_noPmMessage = (
    "✅ **AUTO REPLY - AntiSpam Protection System**\n"
    "I do not allow personal messages {fname}!\n"
    "Tag me in groups first if you want to text me. I'll not reply and you could be automatic blocked.\n"
    "🔐 — <code>All messages here was forwarded to a private log server</code>"
)
blocked_message = bk_blocked_message = (
    "**Você foi bloqueado automaticamente. Não foi falta de aviso. ;)**"
)


async def _init() -> None:
    global noPmMessage, blocked_message  # pylint: disable=global-statement
    async for chat in ALLOWED_COLLECTION.find({"status": "allowed"}):
        Config.ALLOWED_CHATS.add(chat.get("_id"))
    _pm = await SAVED_SETTINGS.find_one({"_id": "PM GUARD STATUS"})
    if _pm:
        Config.ALLOW_ALL_PMS = bool(_pm.get("data"))
    _pmMsg = await SAVED_SETTINGS.find_one({"_id": "NPM Mensagem Personalizada"})
    if _pmMsg:
        noPmMessage = _pmMsg.get("data")
    _blockPmMsg = await SAVED_SETTINGS.find_one(
        {"_id": "Mensagem Personalizada de Block PM"}
    )
    if _blockPmMsg:
        blocked_message = _blockPmMsg.get("data")


@userge.on_cmd(
    "allow",
    about={
        "título": "Aprove as mensagens de alguém que conversa por PM",
        "descrição": "Isto irá permitir receber as menssagens, "
        "e o bot não irá interferir nas mensagens.",
        "como usar": "{tr}permitir [username | userID]\nresponda {tr}permitir em uma mensagem, "
        "ou simplesmente digite o comando {tr}permitir na conversa.",
    },
    allow_channels=False,
    allow_via_bot=False,
)
async def allow(message: Message):
    """Permite o Envio de PM"""
    userid = await get_id(message)
    if userid:
        if userid in pmCounter:
            del pmCounter[userid]
        Config.ALLOWED_CHATS.add(userid)
        a = await ALLOWED_COLLECTION.update_one(
            {"_id": userid}, {"$set": {"status": "allowed"}}, upsert=True
        )
        if a.matched_count:
            await message.edit("`Configurado para receber PM`", del_in=3)
        else:
            await (await userge.get_users(userid)).unblock()
            await message.edit("✅ Suas mensagens foram aprovadas", del_in=5)

        if userid in PMPERMIT_MSG:
            await userge.delete_messages(userid, message_ids=PMPERMIT_MSG[userid])
            del PMPERMIT_MSG[userid]

    else:
        await message.edit(
            "Preciso responder um usuário ou forneça user/id em uma conversa particular",
            del_in=3,
        )


@userge.on_cmd(
    "nopm",
    about={
        "título": "Ativa o bloqueio de mensagens",
        "descrição": "Configuração já intuitiva, "
        "O bot não irá interferir nas mensagens, usuário ficará bloqueado.",
        "flags": {
            "-all": "desaprova todos",
        },
        "como usar": "{tr}bloquear [username | userID]\nresponda {tr}bloquear em uma mensagem, "
        "ou {tr}bloquear em uma conversa particular",
    },
    allow_channels=False,
    allow_via_bot=False,
)
async def denyToPm(message: Message):
    """Não permite PM"""
    if "-all" in message.flags:
        await message.edit("`Proibido de enviar PMs.`")
        one = 0
        while True:
            try:
                usr = list(Config.ALLOWED_CHATS)[one]
                one += 1
            except BaseException:
                break
            try:
                Config.ALLOWED_CHATS.remove(usr)
                await ALLOWED_COLLECTION.delete_one({"_id": usr})
            except BaseException:
                pass
        if not Config.ALLOWED_CHATS:
            await message.edit("`Não alerou nada.`", del_in=3)
        else:
            await message.edit(
                "`Preciso responder um usuário ou forneça user/id em uma conversa particular.`",
                del_in=3,
            )
        return
    userid = await get_id(message)
    if userid:
        if userid in Config.ALLOWED_CHATS:
            Config.ALLOWED_CHATS.remove(userid)
        a = await ALLOWED_COLLECTION.delete_one({"_id": userid})
        if a.deleted_count:
            await message.edit("`Proibido de enviar PMs.`", del_in=3)
        else:
            await message.edit("`Não alerou nada.`", del_in=3)
    else:
        await message.edit(
            "Preciso responder um usuário ou forneça user/id em uma conversa particular",
            del_in=3,
        )


async def get_id(message: Message):
    userid = None
    if message.chat.type in ["private", "bot"]:
        userid = message.chat.id
    if message.reply_to_message:
        userid = message.reply_to_message.from_user.id
    if message.input_str:
        user = message.input_str.lstrip("@")
        try:
            userid = (await userge.get_users(user)).id
        except Exception as e:
            await message.err(str(e))
    return userid


@userge.on_cmd(
    "pmguard",
    about={
        "header": "Switchs the pm permiting module on",
        "description": "This is switched off in default. "
        "You can switch pmguard On or Off with this command. "
        "When you turn on this next time, "
        "the previously allowed chats will be there !",
    },
    allow_channels=False,
)
async def pmguard(message: Message):
    """enable or disable auto pm handler"""
    global pmCounter  # pylint: disable=global-statement
    if Config.ALLOW_ALL_PMS:
        Config.ALLOW_ALL_PMS = False
        await message.edit("`PM Guard ATIVO`", del_in=3, log=__name__)
    else:
        Config.ALLOW_ALL_PMS = True
        await message.edit("`PM Guard DESATIVADO`", del_in=3, log=__name__)
        pmCounter.clear()
    await SAVED_SETTINGS.update_one(
        {"_id": "PM GUARD STATUS"},
        {"$set": {"data": Config.ALLOW_ALL_PMS}},
        upsert=True,
    )


@userge.on_cmd(
    "salvarpm",
    about={
        "header": "Sets the reply message",
        "description": "You can change the default message which userge gives on un-invited PMs",
        "flags": {"-r": "reset to default"},
        "options": {
            "{fname}": "add first name",
            "{lname}": "add last name",
            "{flname}": "add full name",
            "{uname}": "username",
            "{chat}": "chat name",
            "{mention}": "mention user",
        },
    },
    allow_channels=False,
)
async def set_custom_nopm_message(message: Message):
    """setup custom pm message"""
    global noPmMessage  # pylint: disable=global-statement
    if "-r" in message.flags:
        await message.edit("`Mensagem de NOPM resetada!`", del_in=3, log=True)
        noPmMessage = bk_noPmMessage
        await SAVED_SETTINGS.find_one_and_delete({"_id": "CUSTOM NOPM MESSAGE"})
    else:
        string = message.input_or_reply_raw
        if string:
            await message.edit(
                "`Mensagem de NOPM personalizada salva!`", del_in=3, log=True
            )
            noPmMessage = string
            await SAVED_SETTINGS.update_one(
                {"_id": "CUSTOM NOPM MESSAGE"}, {"$set": {"data": string}}, upsert=True
            )
        else:
            await message.err("Falha na Matrix!")


@userge.on_cmd(
    "salvarpmb",
    about={
        "header": "Sets the block message",
        "description": "You can change the default blockPm message "
        "which userge gives on un-invited PMs",
        "flags": {"-r": "reset to default"},
        "options": {
            "{fname}": "add first name",
            "{lname}": "add last name",
            "{flname}": "add full name",
            "{uname}": "username",
            "{chat}": "chat name",
            "{mention}": "mention user",
        },
    },
    allow_channels=False,
)
async def set_custom_blockpm_message(message: Message):
    """setup custom blockpm message"""
    global blocked_message  # pylint: disable=global-statement
    if "-r" in message.flags:
        await message.edit("`Mensagem de BLOCKPM resetada`", del_in=3, log=True)
        blocked_message = bk_blocked_message
        await SAVED_SETTINGS.find_one_and_delete({"_id": "CUSTOM BLOCKPM MESSAGE"})
    else:
        string = message.input_or_reply_raw
        if string:
            await message.edit(
                "`Mensagem de BLOCKPM personalizada salva!`", del_in=3, log=True
            )
            blocked_message = string
            await SAVED_SETTINGS.update_one(
                {"_id": "CUSTOM BLOCKPM MESSAGE"},
                {"$set": {"data": string}},
                upsert=True,
            )
        else:
            await message.err("Falha na Matrix!")


@userge.on_cmd(
    "vpmmsg",
    about={"header": "Displays the reply message for uninvited PMs"},
    allow_channels=False,
)
async def view_current_noPM_msg(message: Message):
    """view current pm message"""
    reply = message.reply_to_message
    if reply:
        reply_to = reply.message_id
    else:
        reply_to = message.message_id
    await message.edit(f"--Current PM message is as below--👇")
    await userge.send_message(
        message.chat.id, noPmMessage, reply_to_message_id=reply_to
    )


@userge.on_cmd(
    "vpm",
    about={"header": "Displays the reply message for blocked PMs"},
    allow_channels=False,
)
async def view_current_blockPM_msg(message: Message):
    """view current block pm message"""
    reply = message.reply_to_message
    if reply:
        reply_to = reply.message_id
    else:
        reply_to = message.message_id
    await message.edit(f"--Mensagem Automática de PM atual")
    await userge.send_message(
        message.chat.id, blocked_message, reply_to_message_id=reply_to
    )


@userge.on_filters(
    ~allowAllFilter
    & filters.incoming
    & filters.private
    & ~filters.bot
    & ~filters.me
    & ~filters.service
    & ~Config.ALLOWED_CHATS,
    allow_via_bot=False,
    group=-1,
)
async def uninvitedPmHandler(message: Message):
    """pm message handler"""
    me = await userge.get_me()
    owner = " ".join([me.first_name, me.last_name or ""])
    user_dict = await userge.get_user_dict(message.from_user.id)
    user_dict.update({"chat": message.chat.title or owner or "this group"})
    if message.from_user.is_verified:
        return
    if message.from_user.id in pmCounter:
        if pmCounter[message.from_user.id] > 3:
            del pmCounter[message.from_user.id]
            # await message.reply(blocked_message)
            report_img_ = await reported_user_image(message.from_user.first_name)
            await userge.send_photo(
                message.chat.id, report_img_, caption=blocked_message
            )
            await message.from_user.block()
            await asyncio.sleep(1)
            await CHANNEL.log(
                f"#BLOCKED\n{user_dict['mention']} has been blocked due to spamming in pm !! "
            )
        else:
            pmCounter[message.from_user.id] += 1
            await message.reply(
                f"You have {pmCounter[message.from_user.id]} out of 4 **Warnings**\n"
                "Please wait until you get approved to pm !",
                del_in=5,
            )
    else:
        pmCounter.update({message.from_user.id: 1})
        PMPERMIT_MSG[message.from_user.id] = (
            await message.reply(
                noPmMessage.format_map(SafeDict(**user_dict))
                + "\n`- AppleBot Security`"
            )
        ).message_id
        await asyncio.sleep(1)
        await CHANNEL.log(
            f"NOVA MENSAGEM #NPM\n{user_dict['mention']} enviou uma mensagem para você."
        )


@userge.on_filters(
    ~allowAllFilter & filters.outgoing & filters.private & ~Config.ALLOWED_CHATS,
    allow_via_bot=False,
)
async def outgoing_auto_approve(message: Message):
    """outgoing handler"""
    userID = message.chat.id
    if userID in pmCounter:
        del pmCounter[userID]
    Config.ALLOWED_CHATS.add(userID)
    await ALLOWED_COLLECTION.update_one(
        {"_id": userID}, {"$set": {"status": "allowed"}}, upsert=True
    )
    user_dict = await userge.get_user_dict(userID)
    await CHANNEL.log(f"**APROVAÇÃO AUTOMÁTICA #AUTOPM**\n{user_dict['mention']}")
