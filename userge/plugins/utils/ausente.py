""" Configuração para o modo ausente """
# VERSÃO DO @APPLLED PARA AFK

import asyncio
import random
import time
from random import choice, randint

from userge import Config, Message, filters, get_collection, userge
from userge.utils import time_formatter

CHANNEL = userge.getCLogger(__name__)
SAVED_SETTINGS = get_collection("CONFIGS")
AFK_COLLECTION = get_collection("AFK")

IS_AFK = False
IS_AFK_FILTER = filters.create(lambda _, __, ___: bool(IS_AFK))
REASON = ""
TIME = 0.0
USERS = {}

# Utilize este linha para adaptar suas medias no Modo Ausente
STATUS = (
    "[\u200c](https://telegra.ph/file/885d526a6d02910e436ef.gif)",
    "[\u200c](https://telegra.ph/file/d432a65c7cfbef904c4b3.gif)",
    "[\u200c](https://telegra.ph/file/39bc79c08ddb42fd6c345.gif)",
    "[\u200c](https://telegra.ph/file/3c4911c20428bd25c8d2e.gif)",
    "[\u200c](https://telegra.ph/file/c4ca2b498c395794baf71.gif)",
    "[\u200c](https://telegra.ph/file/6fa1148a78b3d714b3357.gif)",
    "[\u200c](https://telegra.ph/file/ec1303206f56f03c337d9.gif)",
    "[\u200c](https://telegra.ph/file/b810bbbe02a1b9ad3b77c.gif)",
)


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
        "descrição": "Este modo vai informar sua ausência e respondará à todos que te mencionar. \n"
        "Informará o motivo e o tempo de ausência.",
        "Como usar": "{tr}fui ou {tr}fui [motivo]",
    },
    allow_channels=False,
)
async def active_afk(message: Message) -> None:
    """Modo ausente ligado/desligado"""
    global REASON, IS_AFK, TIME  # pylint: disable=global-statement
    IS_AFK = True
    TIME = time.time()
    REASON = message.input_str
    await asyncio.gather(
        CHANNEL.log(f"Sumindo! : `{REASON}`"),
        message.edit("`Fui!`", del_in=1),
        AFK_COLLECTION.drop(),
        SAVED_SETTINGS.update_one(
            {"_id": "AFK"},
            {"$set": {"on": True, "data": REASON, "time": TIME}},
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
    if user_id in USERS:
        if not (USERS[user_id][0] + USERS[user_id][1]) % randint(2, 4):
            if REASON:
                out_str = (
                    f"⚡️ **Auto Reply** ⒶⒻⓀ \n🕑 **Last Check:**  {afk_time} ago\n"
                    f"▫️ **Status**: {REASON} {random.choice(STATUS)}"
                )
            else:
                out_str = choice(AUTO_AFK)
            coro_list.append(message.reply(out_str))
        if chat.type == "private":
            USERS[user_id][0] += 1
        else:
            USERS[user_id][1] += 1
    else:
        if REASON:
            out_str = (
                f"⚡️ **Auto Reply** ⒶⒻⓀ \n🕑 **Last Check:**  {afk_time} ago\n"
                f"▫️ **Status**: {REASON} {random.choice(STATUS)}"
            )
        else:
            out_str = choice(AUTO_AFK)
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
                p_msg += f"👤 {men} ✉️ **{pcount}**"
                p_count += pcount
            if gcount:
                g_msg += f"👥 {men} ✉️ **{gcount}**"
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
            out_str += f"**Mensagens Privadas:** {p_count}\n {p_msg}"
        if g_count:
            out_str += f"**Mensagens em Grupo:** {g_count}\n {g_msg}"
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

    # Não precisa definir o motivo, apenas faça o comando e vá dormir #


AUTO_AFK = (
    "⚡️ **Auto Reply** ╰• SNOOZE \n🕑 **Last Check:**   10 years ago\n▫️ **Status**:  Zzzz [\u200c](https://telegra.ph/file/3e4a8e757b9059de07d89.gif)",
    "⚡️ **Auto Reply** ╰• SNOOZE \n🕑 **Last Check:**   15 years ago\n▫️ **Status**:  Zzzz [\u200c](https://telegra.ph/file/f68688e04a8713174bb7d.gif)",
    "⚡️ **Auto Reply** ╰• SNOOZE \n🕑 **Last Check:**   Unlimited time ago\n▫️ **Status**:  Zzzz [\u200c](https://telegra.ph/file/885d526a6d02910e436ef.gif)",
)
