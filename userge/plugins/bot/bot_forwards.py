# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.

"""Encaminhamento de Mensagens do Bot"""

import asyncio
from math import floor
from time import time

from pyrogram import filters
from pyrogram.errors import (
    BadRequest,
    FloodWait,
    Forbidden,
    PeerIdInvalid,
    UserIsBlocked,
)

from userge import Config, Message, get_collection, userge
from userge.utils import mention_html, time_formatter
from userge.utils.extras import BotChat

LOG = userge.getLogger(__name__)
CHANNEL = userge.getCLogger(__name__)
BOT_BAN = get_collection("BOT_BAN")
BOT_START = get_collection("BOT_START")
SAVED_SETTINGS = get_collection("CONFIGS")
BOT_MSGS = BotChat("bot_forwards.csv")


async def _init() -> None:
    data = await SAVED_SETTINGS.find_one({"_id": "BOT_FORWARDS"})
    if data:
        Config.BOT_FORWARDS = bool(data["is_active"])


allowForwardFilter = filters.create(lambda _, __, ___: Config.BOT_FORWARDS)
ownersFilter = filters.user(list(Config.OWNER_ID))


@userge.on_cmd(
    "botfwd",
    about={"header": "ative / desative o encaminhamento de mensagens do Bot"},
    allow_channels=False,
)
async def bot_fwd_(message: Message):
    """ative / desative BF"""
    if Config.BOT_FORWARDS:
        Config.BOT_FORWARDS = False
        await message.edit(
            "`Encaminhamento de Mensagens desativado!`", del_in=3, log=__name__
        )
    else:
        Config.BOT_FORWARDS = True
        await message.edit(
            "`Encaminhamento de Mensagens ativado!`", del_in=3, log=__name__
        )
    await SAVED_SETTINGS.update_one(
        {"_id": "BOT_FORWARDS"},
        {"$set": {"is_active": Config.BOT_FORWARDS}},
        upsert=True,
    )


if userge.has_bot:

    @userge.bot.on_message(
        allowForwardFilter
        & ~ownersFilter
        & filters.private
        & filters.incoming
        & ~filters.command("start")
    )
    async def forward_bot(_, message: Message):
        try:
            msg = await message.forward(Config.OWNER_ID[0])
        except UserIsBlocked:
            await CHANNEL.log("**ERRO**: Você bloqueiou seu Bot, dá um /start nele")
        except Exception as new_m_e:
            await CHANNEL.log(
                f"Não foi possível enviar uma mensagem para __ID__: {Config.OWNER_ID[0]}"
                "\n**Nota:** A mensagem será enviada somente para `OWNER_ID`"
                f"\n\n**ERRO:** `{new_m_e}`"
            )
        else:
            BOT_MSGS.store(msg.message_id, message.from_user.id)

    @userge.bot.on_message(
        allowForwardFilter
        & filters.user(Config.OWNER_ID[0])
        & filters.private
        & filters.reply
        & ~filters.regex(
            pattern=f"^(/.+|\{Config.SUDO_TRIGGER}(spoiler|cbutton)\s(.+)?)"
        ),
    )
    async def forward_reply(_, message: Message):
        reply = message.reply_to_message
        to_copy = not message.poll
        user_fwd = reply.forward_from
        if user_fwd:
            # Incase message is your own forward
            if user_fwd.id in Config.OWNER_ID:
                return
            user_id = user_fwd.id
        else:
            if not reply.forward_sender_name:
                return
            if not (user_id := BOT_MSGS.search(reply.message_id)):
                await userge.bot.send_message(
                    Config.OWNER_ID[0],
                    "`Você não pode responder a mensagens antigas"
                    "Privacidade de encaminhamento está ativada`",
                    del_in=3,
                )
                return
        try:
            if to_copy:
                await message.copy(user_id)
            else:
                await message.forward(user_id)
        except UserIsBlocked:
            await message.err(
                "Você não pode responder este usuário porque seu bot o bloqueou!",
                del_in=5,
            )
        except Exception as fwd_e:
            LOG.error(fwd_e)

    @userge.bot.on_message(
        filters.user(Config.OWNER_ID[0])
        & filters.private
        & filters.incoming
        & filters.regex(pattern=r"^/ban\s+(.*)")
    )
    async def bot_ban_(_, message: Message):
        """Banir um usuário a partir do Bot"""
        start_ban = await userge.bot.send_message(message.chat.id, "`Banindo...`")
        user_id, reason = extract_content(message)  # Ban ID & Motivo
        if not user_id:
            await start_ban.err("ID de Usuário não encontrado", del_in=10)
            return
        if not reason:
            await message.err("Banimento Interrompido! Forneça um motivo, né?!")
            return
        ban_user = await userge.bot.get_user_dict(user_id, attr_dict=True)
        if ban_user.id in Config.OWNER_ID:
            await start_ban.edit("Não posso banir o meu próprio deus <3")
            return
        if ban_user.id in Config.SUDO_USERS:
            await start_ban.edit(
                "Este usuário está na sua lista de Sudo,"
                "Portanto, não posso banir essa desgraça com o bot\n"
                "\n**Dica:** Remova essa peste do Sudo.",
                del_in=4,
            )
            return
        if found := await BOT_BAN.find_one({"user_id": ban_user.id}):
            await start_ban.edit(
                "**#BanidoPeloBOT**\n\n"
                "Usuário já na lista de banidos do Bot.\n"
                f"**Motivo do Banimento:** `{found.get('reason')}`",
                del_in=5,
            )
        else:
            await start_ban.edit(await ban_from_bot_pm(ban_user, reason), log=__name__)

    async def ban_from_bot_pm(ban_user, reason: str, log: str = False) -> None:
        user_ = await userge.bot.get_user_dict(ban_user, attr_dict=True)
        banned_msg = (
            f"<i>**Você acabou de ser banindo para sempre, rsrs.**"
            f"</i>\n**Motivo**: {reason}"
        )
        await asyncio.gather(
            BOT_BAN.insert_one(
                {"firstname": user_.fname, "user_id": user_.id, "reason": reason}
            ),
            userge.bot.send_message(user_.id, banned_msg),
        )
        info = (
            r"\\**#UsersBanidosBOTPM**//"
            f"\n\n👤 {user_.mention}\n"
            f"**Nome:** {user_.fname}\n"
            f"**ID do Usuário:** `{user_.id}`\n**Motivo:** `{reason}`"
        )
        if log:
            await userge.getCLogger(log).log(info)
        return info

    @userge.bot.on_message(
        allowForwardFilter
        & filters.user(list(Config.OWNER_ID))
        & filters.private
        & filters.command("broadcast")
    )
    async def broadcast_(_, message: Message):
        replied = message.reply_to_message
        if not replied:
            await message.reply("Responda uma mensagem para encaminhar para geral!")
            return
        start_ = time()
        br_cast = await replied.reply("Enviando sua solicitação...")
        blocked_users = []
        count = 0
        to_copy = not replied.poll
        bot_users_count = await BOT_START.estimated_document_count()
        async for c in BOT_START.find():
            try:
                b_id = c["user_id"]
                if b_id in Config.OWNER_ID:
                    await BOT_START.find_one_and_delete({"user_id": b_id})
                else:
                    await userge.bot.send_message(
                        b_id, "🔊 Você recebeu uma **nova** mensagem."
                    )
                    if to_copy:
                        await replied.copy(b_id)
                    else:
                        await replied.forward(b_id)
                    await asyncio.sleep(0.8)
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except (BadRequest, Forbidden):
                blocked_users.append(
                    BOT_START.find_one_and_delete({"user_id": b_id})
                )  # coro list of removing users
            except Exception as err:
                await CHANNEL.log(str(err))
            else:
                count += 1
                if count % 5 == 0:
                    try:
                        prog_ = (
                            "🔊 Encaminhando...\n\n"
                            + progress_str(
                                total=bot_users_count,
                                current=count + len(blocked_users),
                            )
                            + f"\n\n• ✔️ **Feito** :  `{count}`\n"
                            + f"• ✖️ **Erro** :  `{len(blocked_users)}`"
                        )
                        await br_cast.edit(prog_)
                    except FloodWait as e:
                        await asyncio.sleep(e.x)
        end_ = time()
        b_info = f"🔊  Pronto, mensagem enviara para ➜  <b>{count} usuários.</b>"
        if len(blocked_users) != 0:
            b_info += f"\n🚫  <b>{len(blocked_users)} usuários</b> estão com block no seu bot, então foram removidos."
        b_info += (
            f"\n⏳  <code>Este processo levou: {time_formatter(end_ - start_)}</code>."
        )
        await br_cast.edit(b_info, log=__name__)
        if blocked_users:
            await asyncio.gather(*blocked_users)

    @userge.bot.on_message(
        filters.user(Config.OWNER_ID[0])
        & filters.private
        & filters.reply
        & filters.command("uinfo")
    )
    async def uinfo_(_, message: Message):
        reply = message.reply_to_message
        user_ = None
        if not reply:
            await message.reply("Reply to a message to see user info")
            return
        info_msg = await message.reply("`🔎 Searching for this user in my database ...`")
        if uid_from_db := BOT_MSGS.search(reply.message_id):
            try:
                user_ = await userge.bot.get_user_dict(uid_from_db, attr_dict=True)
            except Exception:
                pass
        elif user_from_fwd := reply.forward_from:
            user_ = await userge.bot.get_user_dict(user_from_fwd, attr_dict=True)

        if not user_:
            return await message.edit(
                "**ERROR:** `Sorry !, Can't Find this user in my database :(`", del_in=3
            )
        uinfo = (
            "**#User_Info**"
            f"\n\n👤 {user_.mention}\n"
            f"**First Name:** {user_.fname}\n"
            f"**User ID:** `{user_.id}`"
        )
        await info_msg.edit(uinfo)


def extract_content(msg: Message):  # Modified a bound method
    id_reason = msg.matches[0].group(1)
    replied = msg.reply_to_message
    user_id, reason = None, None
    if replied:
        fwd = replied.forward_from
        if fwd and id_reason:
            user_id = fwd.id
            reason = id_reason
        if replied.forward_sender_name and id_reason:
            reason = id_reason
            user_id = BOT_MSGS.search(replied.message_id)
    else:
        if id_reason:
            data = id_reason.split(maxsplit=1)
            # Grab First Word and Process it.
            if len(data) == 2:
                user, reason = data
            elif len(data) == 1:
                user = data[0]
            # if user id, convert it to integer
            if user.isdigit():
                user_id = int(user)
            # User @ Mention.
            if user.startswith("@"):
                user_id = user
    return user_id, reason


@userge.on_cmd(
    "bblist",
    about={
        "header": "Get a List of Bot Banned Users",
        "description": "Get Up-to-date list of users Bot Banned by you.",
        "examples": "{tr}bblist",
    },
    allow_channels=False,
)
async def list_bot_banned(message: Message):
    """view Bot Banned users"""
    msg = ""
    async for c in BOT_BAN.find():
        msg += (
            "**User** : "
            + str(c["firstname"])
            + "-> with **User ID** -> "
            + str(c["user_id"])
            + " is **Bot Banned for** : "
            + str(c["reason"])
            + "\n\n"
        )

    await message.edit_or_send_as_file(
        f"**--Bot Banned Users List--**\n\n{msg}" if msg else "`bblist empty!`"
    )


@userge.on_cmd(
    "unbban",
    about={
        "header": "Unban an User from bot",
        "description": "Removes an user from your Bot Ban List",
        "examples": "{tr}unbban [userid]",
    },
    allow_channels=False,
    allow_bots=True,
)
async def ungban_user(message: Message):
    """unban a user from Bot's PM"""
    await message.edit("`UN-BOT Banning ...`")
    user_id = message.input_str
    if not user_id:
        await message.err("No input found !")
        return
    user_id = message.input_str.split()[0].strip()
    try:
        get_mem = await message.client.get_user_dict(user_id)
    except (PeerIdInvalid, IndexError):
        firstname = "Not Known !"
        if user_id.isdigit():
            user_id = int(user_id)
        else:
            await message.err("User Not Known !, Provide a User ID to search.")
            return
    else:
        firstname = get_mem["fname"]
        user_id = get_mem["id"]
    found = await BOT_BAN.find_one({"user_id": user_id})
    if not found:
        await message.err("User Not Found in My Bot Ban List")
        return
    await asyncio.gather(
        BOT_BAN.delete_one(found),
        message.edit(
            r"\\**#Bot_UnBanned_User**//"
            f"\n\n  **First Name:** {mention_html(user_id, firstname)}"
            f"\n  **User ID:** `{user_id}`"
        ),
    )


@userge.on_cmd(
    "bot_forwards", about={"header": "Help regarding commands for bot forwards"}
)
async def bf_help(message: Message):
    """See this For Help"""
    cmd_ = Config.CMD_TRIGGER
    bot_forwards_help = f"""
        **Available Commands**

    [Toggle]
• `{cmd_}bot_fwd` - Enable / Disable bot Forwards

    <i>works **only in** bot pm</i>
• `/ban` - Ban a User from Bot PM
    e.g-
    /ban [reply to forwarded message with reason]
    /ban [user_id/user_name] reason

• `/broadcast` - Send a Broadcast Message to Users in your `{cmd_}bot_users`
    e.g-
    /broadcast [reply to a message]

• `/uinfo` - Get user Info
    e.g-
    /uinfo [reply to forwarded message]

    <i>can work outside bot pm</i>
• `{cmd_}bblist` - BotBanList (Users Banned from your Bot's PM)
    e.g-
    {cmd_}bblist

• `{cmd_}unbban` - UnBotBan  (Unban Users that are in BotBanList)
    e.g-
    {cmd_}unbban [user_id/user_name]
    Hint: Check bblist for banned users.
"""
    await message.edit(bot_forwards_help, del_in=60)


def progress_str(total: int, current: int) -> str:
    percentage = current * 100 / total
    prog_arg = "**Progress** : `{}%`\n" "```[{}{}]```"
    return prog_arg.format(
        percentage,
        "".join((Config.FINISHED_PROGRESS_STR for i in range(floor(percentage / 5)))),
        "".join(
            (Config.UNFINISHED_PROGRESS_STR for i in range(20 - floor(percentage / 5)))
        ),
    )
