"""Bot morreu?"""

import asyncio
import random
from datetime import datetime
from re import compile as comp_regex

from pyrogram import filters
from pyrogram.errors import BadRequest, FloodWait, Forbidden, MediaEmpty
from pyrogram.file_id import PHOTO_TYPES, FileId
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from userge import Config, Message, userge
from userge.core.ext import RawClient
from userge.utils import get_file_id, rand_array

_ALIVE_REGEX = comp_regex(
    r"http[s]?://(i\.imgur\.com|telegra\.ph/file|t\.me)/(\w+)(?:\.|/)(gif|jpg|png|jpeg|[0-9]+)(?:/([0-9]+))?"
)
_USER_CACHED_MEDIA, _BOT_CACHED_MEDIA = None, None

LOGGER = userge.getLogger(__name__)


async def _init() -> None:
    global _USER_CACHED_MEDIA, _BOT_CACHED_MEDIA
    if Config.ALIVE_MEDIA and Config.ALIVE_MEDIA.lower() != "false":
        am_type, am_link = await Bot_Alive.check_media_link(Config.ALIVE_MEDIA.strip())
        if am_type and am_type == "tg_media":
            try:
                if Config.HU_STRING_SESSION:
                    _USER_CACHED_MEDIA = get_file_id(
                        await userge.get_messages(am_link[0], am_link[1])
                    )
            except Exception as u_rr:
                LOGGER.debug(u_rr)
            try:
                if userge.has_bot:
                    _BOT_CACHED_MEDIA = get_file_id(
                        await userge.bot.get_messages(am_link[0], am_link[1])
                    )
            except Exception as b_rr:
                LOGGER.debug(b_rr)


@userge.on_cmd(
    "alive",
    about={"header": "Faça o comando para saber se seu bot tá online"},
    allow_channels=False,
)
async def alive_inline(message: Message):
    try:
        if message.client.is_bot:
            await send_alive_message(message)
        elif userge.has_bot:
            try:
                await send_inline_alive(message)
            except BadRequest:
                await send_alive_message(message)
        else:
            await send_alive_message(message)
    except Exception as e_all:
        await message.err(str(e_all), del_in=10, log=__name__)


async def send_inline_alive(message: Message) -> None:
    _bot = await userge.bot.get_me()
    try:
        i_res = await userge.get_inline_bot_results(_bot.username, "alive")
        i_res_id = (
            (
                await userge.send_inline_bot_result(
                    chat_id=message.chat.id,
                    query_id=i_res.query_id,
                    result_id=i_res.results[0].id,
                )
            )
            .updates[0]
            .id
        )
    except (Forbidden, BadRequest) as ex:
        await message.err(str(ex), del_in=5)
        return
    await message.delete()
    await asyncio.sleep(200)
    await userge.delete_messages(message.chat.id, i_res_id)


async def send_alive_message(message: Message) -> None:
    global _USER_CACHED_MEDIA, _BOT_CACHED_MEDIA
    chat_id = message.chat.id
    client = message.client
    caption = Bot_Alive.alive_info()
    if client.is_bot:
        reply_markup = Bot_Alive.alive_buttons()
        file_id = _BOT_CACHED_MEDIA
    else:
        reply_markup = None
        file_id = _USER_CACHED_MEDIA
        caption += (
            f"\n⚡️  <a href={Config.UPSTEAM_REPO}><b>REPO</b></a>"
            "    <code>|</code>    "
            "👥  <a href='https://t.me/xapplebot'><b>SUPPORT</b></a>"
        )
    if not Config.ALIVE_MEDIA:
        await client.send_photo(
            chat_id,
            photo=Bot_Alive.alive_default_imgs(),
            caption=caption,
            reply_markup=reply_markup,
        )
        return
    url_ = Config.ALIVE_MEDIA.strip()
    if url_.lower() == "false":
        await client.send_message(
            chat_id,
            caption=caption,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )
    else:
        type_, media_ = await Bot_Alive.check_media_link(Config.ALIVE_MEDIA)
        if type_ == "url_gif":
            await client.send_animation(
                chat_id,
                animation=url_,
                caption=caption,
                reply_markup=reply_markup,
            )
        elif type_ == "url_image":
            await client.send_photo(
                chat_id,
                photo=url_,
                caption=caption,
                reply_markup=reply_markup,
            )
        elif type_ == "tg_media":
            try:
                await client.send_cached_media(
                    chat_id,
                    file_id=file_id,
                    caption=caption,
                    reply_markup=reply_markup,
                )
            except MediaEmpty:
                if not message.client.is_bot:
                    try:
                        refeshed_f_id = get_file_id(
                            await userge.get_messages(media_[0], media_[1])
                        )
                        await userge.send_cached_media(
                            chat_id,
                            file_id=refeshed_f_id,
                            caption=caption,
                        )
                    except Exception as u_err:
                        LOGGER.error(u_err)
                    else:
                        _USER_CACHED_MEDIA = refeshed_f_id


if userge.has_bot:

    @userge.bot.on_callback_query(filters.regex(pattern=r"^info_apple$"))
    async def _alive_status(_, c_q: CallbackQuery):
        c_q.from_user.id
        await c_q.answer(
            f"Você é muito gay e curioso!",
            show_alert=True,
        )
        return _alive_status

        # Query para resultado do Primeiro Clique + Gerar Mensagem # Início

    # Pensar no que fazer com isso depois #
    @userge.bot.on_callback_query(filters.regex(pattern=r"^contato_pm$"))
    async def afk_resultado(_, c_q: CallbackQuery):
        c_q.from_user.id
        photo = f"""{random.choice(ANIMTN)}"""
        texto = f"{random.choice(CONTATOS)}\n\n{random.choice(ANIMES)}"
        buttons = [
            [
                InlineKeyboardButton(
                    text="❎ Ok",
                    url="https://t.me/twapple",
                )
            ]
        ]
        try:
            await userge.bot.send_animation(
                message.chat.id,
                animation=photo,
                caption=texto,
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        except MessageNotModified:
            return

    # Query para resultado do Primeiro Clique + Gerar Mensagem # FIM

    @userge.bot.on_callback_query(filters.regex(pattern=r"^settings_btn$"))
    async def alive_cb(_, c_q: CallbackQuery):
        allow = bool(
            c_q.from_user
            and (
                c_q.from_user.id in Config.OWNER_ID
                or c_q.from_user.id in Config.SUDO_USERS
            )
        )
        if allow:
            start = datetime.now()
            try:
                await c_q.edit_message_text(
                    Bot_Alive.alive_info(),
                    reply_markup=Bot_Alive.alive_buttons(),
                    disable_web_page_preview=True,
                )
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except BadRequest:
                pass
            ping = "UPTIME {} sec\n"
        alive_s = "▫️ XtraP : {}\n".format(_parse_arg(Config.LOAD_UNOFFICIAL_PLUGINS))
        alive_s += f"▫️ SUDO : {_parse_arg(Config.SUDO_ENABLED)}\n"
        alive_s += f"▫️ ANTISPAM : {_parse_arg(Config.ANTISPAM_SENTRY)}\n"
        if Config.HEROKU_APP and Config.RUN_DYNO_SAVER:
            alive_s += "⛽️ 𝗗𝘆𝗻𝗼 𝗦𝗮𝘃𝗲𝗿 :  ✅ 𝙴𝚗𝚊𝚋𝚕𝚎𝚍\n"
        alive_s += f"▫️ BOT FWD : {_parse_arg(Config.BOT_FORWARDS)}\n"
        alive_s += f"▫️ M SECURITY : {_parse_arg(not Config.ALLOW_ALL_PMS)}\n"
        alive_s += f"▫️ LOGGER : {_parse_arg(Config.PM_LOGGING)}"
        if allow:
            end = datetime.now()
            m_s = (end - start).microseconds / 1000
            await c_q.answer(ping.format(m_s) + alive_s, show_alert=True)
        else:
            await c_q.answer(alive_s, show_alert=True)
        await asyncio.sleep(0.5)


def _parse_arg(arg: bool) -> str:
    return " ✅ " if arg else " ❌ "


class Bot_Alive:
    @staticmethod
    async def check_media_link(media_link: str):
        match = _ALIVE_REGEX.search(media_link.strip())
        if not match:
            return None, None
        if match.group(1) == "i.imgur.com":
            link = match.group(0)
            link_type = "url_gif" if match.group(3) == "gif" else "url_image"
        elif match.group(1) == "telegra.ph/file":
            link = match.group(0)
            link_type = "url_gif" if match.group(3) == "gif" else "url_image"
        else:
            link_type = "tg_media"
            if match.group(2) == "c":
                chat_id = int("-100" + str(match.group(3)))
                message_id = match.group(4)
            else:
                chat_id = match.group(2)
                message_id = match.group(3)
            link = [chat_id, int(message_id)]
        return link_type, link

    @staticmethod
    def alive_info() -> str:
        alive_info_ = f"""


         """
        return alive_info_

    @staticmethod
    def _get_mode() -> str:
        if RawClient.DUAL_MODE:
            return "Dual"
        if Config.BOT_TOKEN:
            return "Bot"
        return "❌ Git"

    @staticmethod
    def alive_buttons() -> InlineKeyboardMarkup:
        buttons = [
            [
                InlineKeyboardButton(text="❎ STATUS", callback_data="settings_btn"),
                InlineKeyboardButton(text="⁉️", callback_data="info_apple"),
            ],
        ]
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def alive_default_imgs() -> str:
        alive_imgs = [
            "https://telegra.ph/file/241c8b73c8931cd150082.jpg",
            "https://telegra.ph/file/241c8b73c8931cd150082.jpg",
            "https://telegra.ph/file/241c8b73c8931cd150082.jpg",
            "https://telegra.ph/file/241c8b73c8931cd150082.jpg",
            "https://telegra.ph/file/241c8b73c8931cd150082.jpg",
        ]
        return rand_array(alive_imgs)

    @staticmethod
    def get_bot_cached_fid() -> str:
        return _BOT_CACHED_MEDIA

    @staticmethod
    def is_photo(file_id: str) -> bool:
        return bool(FileId.decode(file_id).file_type in PHOTO_TYPES)


TEAM_APPLEBOT = (
    "𝐂𝐇𝐄𝐂𝐊 𝐓𝐇𝐈𝐒:\n\n𝐀𝐩𝐩𝐥𝐞/𝐎𝐫𝐚𝐧𝐠𝐞\n𝙳𝚎𝚟 𝚖𝚊𝚒𝚗\n🔗 @applled\n\n𝐒𝐚𝐦𝐮𝐜𝐚/𝐒𝐚𝐦𝐮𝐞𝐥\n𝙲𝚘𝚗𝚝𝚛𝚒𝚋𝚞𝚝𝚘𝚛\n🔗 @NoteZV\n ",
    # Adicionar mais informações randômicas em breve
)
ANIMTN = (
    "https://telegra.ph/file/7465c70c1cb0f35cc536e.gif",
    "https://telegra.ph/file/b2fda41d76cd798d4c368.gif",
    "https://telegra.ph/file/43901682e8a936d76572e.gif",
    "https://telegra.ph/file/140d286c155894093c250.gif",
    "https://telegra.ph/file/ebfb744d7a25736ef09f5.gif",
)
CONTATOS = (
    "🏷 | 𝐒𝐓𝐀𝐓𝐔𝐒\n ╰• Curioso, né?\n\n<i>Então,\n Você pode entrar em contato comigo diretamentepelo meu bot. Para evitar spam, responderei exclusivamente por ele. Em alguns casos, não terei problemas em enviar mensagens no particular.</i>\n\n🔗 @twapple\n ╰• 𝚁𝚎𝚜𝚎𝚛𝚟𝚊𝚍𝚘 𝚙𝚊𝚛𝚊 𝚙𝚘𝚜𝚝𝚜 𝚊𝚕𝚎𝚊𝚝ó𝚛𝚒𝚘𝚜 𝚍𝚘 @applled",
)
