""" Configuração para o modo ausente - Adaptado por #NoteX/Samuca/Applleb / AppleBot"""

import asyncio
import time
from random import randint
from re import compile as comp_regex

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from userge import Config, Message, filters, get_collection, userge
from userge.utils import time_formatter

_TELE_REGEX = comp_regex(
    r"http[s]?://(i\.imgur\.com|telegra\.ph/file|t\.me)/(\w+)(?:\.|/)(gif|jpg|png|jpeg|mp4|[0-9]+)(?:/([0-9]+))?"
)

CHANNEL = userge.getCLogger(__name__)
SAVED_SETTINGS = get_collection("CONFIGS")
AFK_COLLECTION = get_collection("AFK")

IS_AFK = False
IS_AFK_FILTER = filters.create(lambda _, __, ___: bool(IS_AFK))
REASON = ""
TIME = 0.0
USERS = {}


async def _init() -> None:
    global IS_AFK, REASON, TIME  # pylint: disable=global-statement
    data = await SAVED_SETTINGS.find_one({"_id": "AFK"})
    if data:
        IS_AFK = data["on"]
        REASON = data["data"]
        TIME = data["time"] if "time" in data else 0
    async for _user in AFK_COLLECTION.find():
        USERS.update({_user["_id"]: [_user["pcount"], _user["gcount"], _user["men"]]})


@userge.on_cmd(
    "fui",
    about={
        "header": "Definir status para modo ausente",
        "descrição": "Este modo vai informar sua ausência e respondará à todos que te mencionarem. \n"
        "Informará o motivo e o tempo de ausência.",
        "Como usar": "{tr}fui ou {tr}fui [motivo] | endereço.com/arquivo.gif",
    },
    allow_channels=False,
)
async def active_afk(message: Message) -> None:
    """Modo ausente ligado/desligado"""
    global REASON, IS_AFK, TIME  # pylint: disable=global-statement
    IS_AFK = True
    TIME = time.time()
    REASON = message.input_str
    match_ = _TELE_REGEX.search(REASON)
    if match_:
        r_ = REASON.split(" | ", maxsplit=1)
        STATUS_ = r_[0]
        await asyncio.gather(
            CHANNEL.log(f"Sumindo.. `{STATUS_}` [\u200c]({match_.group(0)})"),
            message.edit("`Fui!`", del_in=1),
            AFK_COLLECTION.drop(),
            SAVED_SETTINGS.update_one(
                {"_id": "AFK"},
                {"$set": {"on": True, "data": STATUS_, "time": TIME}},
                upsert=True,
            ),
        )
    else:
        await asyncio.gather(
            CHANNEL.log(f"Sumindo... `{REASON}`"),
            message.edit("`Fui!`", del_in=1),
            AFK_COLLECTION.drop(),
            SAVED_SETTINGS.update_one(
                {"_id": "AFK"},
                {"set": {"on": True, "data": REASON, "time": TIME}},
                upsert=True,
            ),
        )


@userge.on_filters(
    IS_AFK_FILTER
    & ~filters.me
    & ~filters.bot
    & ~filters.user(Config.TG_IDS)
    & ~filters.edited
    & (
        filters.mentioned
        | (
            filters.private
            & ~filters.service
            & (
                filters.create(lambda _, __, ___: Config.ALLOW_ALL_PMS)
                | Config.ALLOWED_CHATS
            )
        )
    ),
    allow_via_bot=False,
)
async def handle_afk_incomming(message: Message) -> None:
    """Configurações das mensagens automáticas"""
    if not message.from_user:
        return
    user_id = message.from_user.id
    chat = message.chat
    user_dict = await message.client.get_user_dict(user_id)
    afk_time = time_formatter(round(time.time() - TIME))
    coro_list = []

    client = message.client
    chat_id = message.chat.id
    if user_id in USERS:
        if not (USERS[user_id][0] + USERS[user_id][1]) % randint(2, 4):
            match = _TELE_REGEX.search(REASON)
            if match:
                type_, media_ = await _afk_.check_media_link(match.group(0))
                if type_ == "url_gif":
                    r = REASON.split(" | ", maxsplit=1)
                    STATUS = r[0]
                    out_str = (
                        f"🌐 **AUTO REPLY** ⒶⒻⓀ \n ╰•  **Last Seen:** {afk_time} ago\n\n"
                        f"🏷 **I'm not here because:**\n {STATUS}"
                    )
                    await client.send_animation(
                        chat_id,
                        animation=match.group(0),
                        caption=out_str,
                        reply_markup=_afk_.afk_buttons(),
                    )
                elif type_ == "url_image":
                    await client.send_photo(
                        chat_id,
                        photo=match.group(0),
                        caption=_afk_.out_str(),
                        reply_markup=_afk_.afk_buttons(),
                    )
            else:
                out_str = (
                    f"🌐 **AUTO REPLY** ⒶⒻⓀ \n ╰•  **Last Seen:** {afk_time} ago\n\n"
                    f"🏷 **I'm not here because:**\n__{REASON}__"
                )
                coro_list.append(message.reply(out_str))
        if chat.type == "private":
            USERS[user_id][0] += 1
        else:
            USERS[user_id][1] += 1
    else:
        match = _TELE_REGEX.search(REASON)
        if match:
            type_, media_ = await _afk_.check_media_link(match.group(0))
            if type_ == "url_gif":
                r = REASON.split(" | ", maxsplit=1)
                STATUS = r[0]
                out_str = (
                    f"🌐 **AUTO REPLY** ⒶⒻⓀ \n ╰•  **Last Seen:** {afk_time} ago\n\n"
                    f"🏷 **I'm not here because:**\n {STATUS}"
                )
                await client.send_animation(
                    chat_id,
                    animation=match.group(0),
                    caption=out_str,
                    reply_markup=_afk_.afk_buttons(),
                )
            elif type_ == "url_image":
                await client.send_photo(
                    chat_id,
                    photo=match.group(0),
                    caption=_afk_.out_str(),
                    reply_markup=_afk_.afk_buttons(),
                )
        else:
            out_str = (
                f"🌐 **AUTO REPLY** ⒶⒻⓀ \n ╰•  **Last Seen:** {afk_time} ago\n\n"
                f"🏷 **I'm not here because:**\n__{REASON}__"
            )
            coro_list.append(message.reply(out_str))
        if chat.type == "private":
            USERS[user_id] = [1, 0, user_dict["mention"]]
        else:
            USERS[user_id] = [0, 1, user_dict["mention"]]
    if chat.type == "private":
        coro_list.append(
            CHANNEL.log(
                f"Em seu #PRIVADO\n{user_dict['mention']}\n Te enviou a mensagem:\n\n"
                f"{message.text}"
            )
        )
    else:
        coro_list.append(
            CHANNEL.log(
                "#GRUPO\n"
                f"{user_dict['mention']} mencionou você em [{chat.title}](http://t.me/{chat.username})\n\n"
                f"{message.text}\n\n"
                f"[goto_msg](https://t.me/c/{str(chat.id)[4:]}/{message.message_id})"
            )
        )
    coro_list.append(
        AFK_COLLECTION.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "pcount": USERS[user_id][0],
                    "gcount": USERS[user_id][1],
                    "men": USERS[user_id][2],
                }
            },
            upsert=True,
        )
    )
    await asyncio.gather(*coro_list)


class _afk_:
    def out_str() -> str:
        time_formatter(round(time.time() - TIME))
        _r = REASON.split(" | ", maxsplit=1)
        _STATUS = _r[0]
        out_str = (
            f"🌐 **AUTO REPLY** ⒶⒻⓀ \n ╰•  **Last Seen:** {afk_time} ago\n\n"
            f"🏷 **I'm not here because:**\n{_STATUS}"
        )
        return out_str

    async def check_media_link(media_link: str):
        match_ = _TELE_REGEX.search(media_link.strip())
        if not match_:
            return None, None
        if match_.group(1) == "i.imgur.com":
            link = match_.group(0)
            link_type = "url_gif" if match_.group(3) == "gif" else "url_image"
        elif match_.group(1) == "telegra.ph/file":
            link = match_.group(0)
            link_type = "url_gif" if match_.group(3) == "gif" else "url_image"
        else:
            link_type = "tg_media"
            if match_.group(2) == "c":
                chat_id = int("-100" + str(match_.group(3)))
                message_id = match_.group(4)
            else:
                chat_id = match_.group(2)
                message_id = match_.group(3)
            link = [chat_id, int(message_id)]
        return link_type, link

    def afk_buttons() -> InlineKeyboardMarkup:
        buttons = [
            [
                InlineKeyboardButton(text="AppleBot", url=Config.UPSTREAM_REPO),
            ]
        ]
        return InlineKeyboardMarkup(buttons)


@userge.on_filters(IS_AFK_FILTER & filters.outgoing, group=-1, allow_via_bot=False)
async def handle_afk_outgoing(message: Message) -> None:
    """Status detalhado e atualizado sobre seu modo ausente"""
    global IS_AFK  # pylint: disable=global-statement
    IS_AFK = False
    afk_time = time_formatter(round(time.time() - TIME))
    replied: Message = await message.reply("`Não estou mais ausente!`", log=__name__)
    coro_list = []
    if USERS:
        p_msg = ""
        g_msg = ""
        p_count = 0
        g_count = 0
        for pcount, gcount, men in USERS.values():
            if pcount:
                p_msg += f"👤 {men} ✉️ **{pcount}**\n"
                p_count += pcount
            if gcount:
                g_msg += f"👥 {men} ✉️ **{gcount}**\n"
                g_count += gcount
        coro_list.append(
            replied.edit(
                f"`💬 Na sua Inbox: {p_count + g_count} mensagens. "
                f"▫️ Confira os detalhes no log.`\n\n💤 **Ausente por** : __{afk_time}__",
                del_in=1,
            )
        )
        out_str = (
            f"📂 Mensagens na Inbox[:](https://telegra.ph/file/7c1ba52391b7ffcc3e891.png) **{p_count + g_count}** \n▫️ Em contato: **{len(USERS)}** desgraçado(s) "
            + f"\n▫️ **Ausente por** : __{afk_time}__\n\n"
        )
        if p_count:
            out_str += f"\n**{p_count} Mensagens Privadas:**\n\n{p_msg}"
        if g_count:
            out_str += f"\n**{g_count} Mensagens em Grupo:**\n\n{g_msg}"
        coro_list.append(CHANNEL.log(out_str))
        USERS.clear()
    else:
        await asyncio.sleep(3)
        coro_list.append(replied.delete())
    coro_list.append(
        asyncio.gather(
            AFK_COLLECTION.drop(),
            SAVED_SETTINGS.update_one(
                {"_id": "AFK"}, {"$set": {"on": False}}, upsert=True
            ),
        )
    )
    await asyncio.gather(*coro_list)


AFK_REASONS = (
    "⚡️ **Auto Reply** ⒶⒻⓀ ╰• SNOOZE \n🕑 **Last Check:**   10 years ago\n▫️ **Status**:  Zzzz [\u200c](https://telegra.ph/file/3e4a8e757b9059de07d89.gif)",
    "⚡️ **Auto Reply** ⒶⒻⓀ ╰• SNOOZE \n🕑 **Last Check:**   15 years ago\n▫️ **Status**:  Zzzz [\u200c](https://telegra.ph/file/f68688e04a8713174bb7d.gif)",
    "⚡️ **Auto Reply** ⒶⒻⓀ ╰• SNOOZE \n🕑 **Last Check:**   Unlimited time ago\n▫️ **Status**:  Zzzz [\u200c](https://telegra.ph/file/885d526a6d02910e436ef.gif)",
)
