""" Configuração para o modo ausente - Adaptado por #NoteX/Samuca/Applled / AppleBot"""

import asyncio
import random
import time
from random import randint
from re import compile as comp_regex

from pyrogram import filters
from pyrogram.errors import MessageNotModified
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from userge import Config, Message, filters, get_collection, userge
from userge.plugins.utils.afk_inline import *
from userge.utils import time_formatter

_TELE_REGEX = comp_regex(
    r"http[s]?://(i\.imgur\.com|telegra\.ph/file|t\.me)/(\w+)(?:\.|/)(gif|mp4|jpg|png|jpeg|[0-9]+)(?:/([0-9]+))?"
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
    "afk",
    about={
        "header": "Definir status para modo ausente",
        "descrição": "Este modo vai informar sua ausência e respondará à todos que te mencionarem. \n"
        "Informará o motivo e o tempo de ausência.",
        "Como usar": "{tr}afk ou {tr}afk [motivo] | endereço.com/arquivo.gif",
    },
    allow_channels=False,
)
async def ausente(message: Message) -> None:
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
            CHANNEL.log(f"Sumindo! : `{STATUS_}` [\u200c]({match_.group(0)})"),
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
            CHANNEL.log(f"Sumindo!  `{REASON}`"),
            message.edit("`Fuii!`", del_in=1),
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
async def respostas(message: Message) -> None:
    """Configurações das mensagens automáticas"""
    if not message.from_user:
        return
    user_id = message.from_user.id
    chat = message.chat
    user_dict = await message.client.get_user_dict(user_id)
    time_formatter(round(time.time() - TIME))
    coro_list = []
    if user_id in USERS:
        if not (USERS[user_id][0] + USERS[user_id][1]) % randint(2, 4):
            match = _TELE_REGEX.search(REASON)
            if match:
                type_, media_ = await _afk_.check_media_link(match.group(0))
                if type_ == "url_gif":
                    await send_inline_afk(message)
                if type_ == "url_image":
                    await send_inline_afk_(message)
            else:
                coro_list.append(await _send_inline_afk(message))
        if chat.type == "private":
            USERS[user_id][0] += 1
        else:
            USERS[user_id][1] += 1
    else:
        match = _TELE_REGEX.search(REASON)
        if match:
            type_, media_ = await _afk_.check_media_link(match.group(0))
            if type_ == "url_image":
                await send_inline_afk_(message)
            elif type_ == "url_gif":
                await send_inline_afk(message)
        else:
            coro_list.append(await _send_inline_afk(message))
        if chat.type == "private":
            USERS[user_id] = [1, 0, user_dict["mention"]]
        else:
            USERS[user_id] = [0, 1, user_dict["mention"]]
    if chat.type == "private":
        coro_list.append(
            CHANNEL.log(
                f"Em seu #PRIVADO\n{user_dict['mention']}\n Te enviou a mensagem:\n\n"
                f"💬 __{message.text}__"
            )
        )
    else:
        coro_list.append(
            CHANNEL.log(
                "#GRUPO\n"
                f"{user_dict['mention']} mencionou você no grupo: [{chat.title}](http://t.me/{chat.username})\n\n"
                f"  ➖➖➖➖➖➖\n"
                f"  💬 __{message.text}__\n\n"
                f"  ➖➖➖➖➖➖\n"
                f"🔗 [Link](https://t.me/c/{str(chat.id)[4:]}/{message.message_id}) da mensagem."
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
        _afk_time = time_formatter(round(time.time() - TIME))
        _r = REASON.split(" | ", maxsplit=1)
        _STATUS = _r[0]
        out_str = (
            f"🏷 | **AUTO REPLY** ⒶⒻⓀ \n ╰•  **Last Seen:** {_afk_time} ago\n      ➖➖➖➖➖➖\n"
            f"⁉️ | **WHAT'S HAPPENING?**\n {_STATUS}"
        )
        return out_str

    def _out_str() -> str:
        afk_time_ = time_formatter(round(time.time() - TIME))
        out_str = (
            f"🏷 | **AUTO REPLY** ⒶⒻⓀ \n ╰•  **Last Seen:** {afk_time_} ago\n      ➖➖➖➖➖➖\n"
            f"⁉️ | **WHAT'S HAPPENING?**\n▫️ <code>{REASON}</code>"
        )
        return out_str

    def link() -> str:
        _match_ = _TELE_REGEX.search(REASON)
        if _match_:
            link = _match_.group(0)
            return link

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
                InlineKeyboardButton(text="⚡️ STATUS", callback_data="status_afk"),
                InlineKeyboardButton(text="+", callback_data="afk_pm_"),
            ],
        ]
        return InlineKeyboardMarkup(buttons)


@userge.on_filters(IS_AFK_FILTER & filters.outgoing, group=-1, allow_via_bot=False)
async def logs(message: Message) -> None:
    """Detalhes - Log do Modo Ausente"""
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

    # # # teste # # #
    @userge.bot.on_callback_query(filters.regex(pattern=r"^status_afk$"))
    async def status_afk_(_, c_q: CallbackQuery):
        c_q.from_user.id
        await c_q.answer(
            f"🍏 @applled 𝐒𝐓𝐀𝐓𝐔𝐒:\n\n𝐂𝐡𝐚𝐩𝐨𝐥𝐢𝐧 𝐝𝐢𝐬𝐬𝐞:\n ╰• {random.choice(FRASE_AFK)}\n",
            show_alert=True,
        )
        return status_afk_

    # Query para resultado do Primeiro Clique + Gerar Mensagem # Início
    @userge.bot.on_callback_query(filters.regex(pattern=r"^afk_pm_$"))
    async def afk_resultado(_, c_q: CallbackQuery):
        c_q.from_user.id
        texto = f"{random.choice(CONTATO)}"
        photo = f"""{random.choice(ANIMTN)}"""
        buttons = [
            [
                InlineKeyboardButton(
                    text="❎ Mensagem Privada",
                    url="https://t.me/youcantbot",
                )
            ]
        ]
        try:
            await userge.send_inline_bot_result(
                message.chat.id,
                animation=photo,
                caption=texto,
                reply_markup=InlineKeyboardMarkup(buttons),
                del_in=5,
            )
        except MessageNotModified:
            return

    # Query para resultado do Primeiro Clique + Gerar Mensagem # FIM

    @userge.bot.on_callback_query(filters.regex(pattern=r"^status_apple$"))
    async def _status_afk(_, c_q: CallbackQuery):
        c_q.from_user.id
        await c_q.answer(
            f"🍎 @applled 𝐁𝐈𝐎/Projects:\nТак вам любопытно\n\nHi, human!\n{random.choice(BIO_AFK)}\n",
            show_alert=True,
        )
        return _status_afk


ANIMTN = ("https://telegra.ph/file/7465c70c1cb0f35cc536e.gif",)
CONTATO = (
    "🏷 | 𝐒𝐓𝐀𝐓𝐔𝐒\n ╰• 𝙼𝚎𝚗𝚜𝚊𝚐𝚎𝚖 𝚊𝚞𝚝𝚘𝚖𝚊𝚝𝚒𝚌𝚊\n\n<i>Olá,\nVocê pode entrar em contato comigo diretamentepelo meu bot. Para evitar spam, responderei exclusivamente por ele. Em alguns casos, não terei problemas em enviar mensagens no particular.</i>\n\n🔗 @twapple\n ╰• 𝚁𝚎𝚜𝚎𝚛𝚟𝚊𝚍𝚘 𝚙𝚊𝚛𝚊 𝚙𝚘𝚜𝚝𝚜 𝚊𝚕𝚎𝚊𝚝ó𝚛𝚒𝚘𝚜 𝚍𝚘 @applled",
)

FRASE_AFK = (
    "Se você perdeu a batalha,\nimagna a guerra que tem mais pessoas!",
    "As moscas não se arriscariam\nà ir a Roma de boca fechada,\npois morreriam de fome.",
    "Fazer alguém, sem olhar o bem que tem.",
    "Quem ri por último come mais chocolate.",
)
BIO_AFK = (
    "𝐂𝐇𝐄𝐂𝐊 𝐓𝐇𝐈𝐒:\n\n𝐋𝐢𝐤𝐞 𝐓𝐰𝐞𝐞𝐭𝐬\n🔗 @twapple\n𝐁𝐢𝐨\n🔗 @orapple\n ╰• 𝘔𝘰𝘳𝘦 𝘤𝘰𝘮𝘪𝘯𝘨 𝘴𝘰𝘰𝘯...",
    # Adicionar mais coisas
)
AFK_REASONS = (
    "I'm busy right now. Please talk in a bag and when I come back you can just give me the bag!",
)
