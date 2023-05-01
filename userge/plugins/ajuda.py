import os
import random
import re
from math import ceil
from typing import Any, Callable, Dict, List, Union

import ujson
from html_telegraph_poster import TelegraphPoster
from pyrogram import filters
from pyrogram.errors import BadRequest, MessageIdInvalid, MessageNotModified
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultAnimation,
    InlineQueryResultArticle,
    InlineQueryResultCachedDocument,
    InlineQueryResultCachedPhoto,
    InlineQueryResultPhoto,
    InputTextMessageContent,
)
from youtubesearchpython import VideosSearch

from userge import Config, Message, get_collection, userge
from userge.core.ext import RawClient
from userge.utils import get_file_id, get_response
from userge.utils import parse_buttons as pb
from userge.utils import rand_key

from .bot.alive import Bot_Alive
from .bot.gogo import Anime
from .bot.utube_inline import (
    download_button,
    get_yt_video_id,
    get_ytthumb,
    result_formatter,
    ytsearch_data,
)
from .fun.stylish import Styled, font_gen
from .misc.redditdl import reddit_thumb_link
from .orange.afk import _afk_
from .utils.notes import get_inote

CHANNEL = userge.getCLogger(__name__)
CONTATO = (
    "🏷 | 𝐒𝐓𝐀𝐓𝐔𝐒\n ╰• 𝙼𝚎𝚗𝚜𝚊𝚐𝚎𝚖 𝚊𝚞𝚝𝚘𝚖𝚊𝚝𝚒𝚌𝚊\n\n<i>Olá,\n Você pode entrar em contato comigo diretamentepelo meu bot. Para evitar spam, responderei exclusivamente por ele. Em alguns casos, não terei problemas em enviar mensagens no particular.</i>\n\n🔗 @twapple\n ╰• 𝚁𝚎𝚜𝚎𝚛𝚟𝚊𝚍𝚘 𝚙𝚊𝚛𝚊 𝚙𝚘𝚜𝚝𝚜 𝚊𝚕𝚎𝚊𝚝ó𝚛𝚒𝚘𝚜 𝚍𝚘 @applled",
)
_CATEGORY = {
    "Controle": "▫️",
    "Diversão": "▫️",
    "Diveros": "▫️",
    "Ferram": "▫️",
    "Úteis": "▫️",
    "Carregados": "▫️",
    "Breves": "▫️",
    "Plugins": "▫️",
    "Bot": "▫️",
}
# Database
SAVED_SETTINGS = get_collection("CONFIGS")
REPO_X = InlineQueryResultArticle(
    title="Repo",
    input_message_content=InputTextMessageContent("**Não há nada para você aqui"),
    url="https://t.me/laranjudo",
    description="Confire o seu!",
    thumb_url="https://telegra.ph/file/bc5d7d950ce2d1a050ae6.png",
    reply_markup=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "AppleBot para appleeds", url="https://github.com/"
                ),
                InlineKeyboardButton(
                    "Bing ",
                    url=("google.com" "https://apple.com/"),
                ),
            ]
        ]
    ),
)


async def _init() -> None:
    data = await SAVED_SETTINGS.find_one({"_id": "CURRENT_CLIENT"})
    if data:
        Config.USE_USER_FOR_CLIENT_CHECKS = bool(data["is_user"])


@userge.on_cmd(
    "ajuda", about={"header": "Guia de Comandos / AppleBot"}, allow_channels=False
)
async def helpme(message: Message) -> None:
    plugins = userge.manager.enabled_plugins
    if not message.input_str:
        out_str = f"""AppleBot - <b>Plugins Disponíveis:</b> (<code>{len(plugins)}</code>)\n\n"""
        cat_plugins = userge.manager.get_plugins()
        for cat in sorted(cat_plugins):
            if cat == "plugins":
                continue
            out_str += (
                f"  {_CATEGORY.get(cat, '📁')} <b>{cat}</b> "
                f"(<code>{len(cat_plugins[cat])}</code>) :   <code>"
                + "</code>    <code>".join(sorted(cat_plugins[cat]))
                + "</code>\n\n"
            )
        out_str += f"""▫️ <b>Como usar:</b>  <code>{Config.CMD_TRIGGER}ajuda nome do plugin</code>"""
    else:
        key = message.input_str
        if (
            not key.startswith(Config.CMD_TRIGGER)
            and key in plugins
            and (
                len(plugins[key].enabled_commands) > 1
                or plugins[key].enabled_commands[0].name.lstrip(Config.CMD_TRIGGER)
                != key
            )
        ):
            commands = plugins[key].enabled_commands
            out_str = f"""<b><u>(<code>{len(commands)}</code>) Comandos Disponíveis</u></b>

▫️ <b>Plugin:</b>  <code>{key}</code>
▫️ <b>Doc:</b>  <code>{plugins[key].doc}</code>\n\n"""
            for i, cmd in enumerate(commands, start=1):
                out_str += (
                    f"    ▫️ <b>cmd(<code>{i}</code>):</b>  <code>{cmd.name}</code>\n"
                    f"    ▫️ <b>info:</b>  <i>{cmd.doc}</i>\n\n"
                )
            out_str += f"""📕 <b>Como usar:</b>  <code>{Config.CMD_TRIGGER}ajuda comando</code>"""
        else:
            commands = userge.manager.enabled_commands
            key = key.lstrip(Config.CMD_TRIGGER)
            key_ = Config.CMD_TRIGGER + key
            if key in commands:
                out_str = f"<code>{key}</code>\n\n{commands[key].about}"
            elif key_ in commands:
                out_str = f"<code>{key_}</code>\n\n{commands[key_].about}"
            else:
                out_str = f"<i>Nenhum módulo/comando encontrado para</i>: <code>{message.input_str}</code>"
    await message.edit(
        out_str, del_in=0, parse_mode="html", disable_web_page_preview=True
    )


if userge.has_bot:

    def check_owner(func):
        async def wrapper(_, c_q: CallbackQuery):
            if c_q.from_user and (
                c_q.from_user.id
                in Config.OWNER_ID
                # or c_q.from_user.id in Config.SUDO_USERS
            ):
                await c_q.answer()
                try:
                    await func(c_q)
                except MessageNotModified:
                    await c_q.answer(
                        "Não encontrei nada para atualizar.", show_alert=True
                    )
                except MessageIdInvalid:
                    await c_q.answer(
                        "Foi mal, não tenho permissões para editar isso.",
                        show_alert=True,
                    )
            else:
                user_dict = await userge.bot.get_user_dict(Config.OWNER_ID[0])
                await c_q.answer(
                    f"Acesso concedido do AppleBot somente para {user_dict['flname']} ",
                    show_alert=True,
                )

        return wrapper

    @userge.bot.on_callback_query(
        filters.regex(pattern=r"\((.+)\)(next|prev)\((\d+)\)")
    )
    @check_owner
    async def callback_next_prev(callback_query: CallbackQuery):
        cur_pos = str(callback_query.matches[0].group(1))
        n_or_p = str(callback_query.matches[0].group(2))
        p_num = int(callback_query.matches[0].group(3))
        p_num = p_num + 1 if n_or_p == "next" else p_num - 1
        pos_list = cur_pos.split("|")
        if len(pos_list) == 1:
            buttons = parse_buttons(
                p_num,
                cur_pos,
                lambda x: f"{_CATEGORY.get(x, '📁')} {x}",
                userge.manager.get_all_plugins(),
            )
        elif len(pos_list) == 2:
            buttons = parse_buttons(
                p_num,
                cur_pos,
                lambda x: f"▫️ {x}",
                userge.manager.get_all_plugins()[pos_list[-1]],
            )
        elif len(pos_list) == 3:
            _, buttons = plugin_data(cur_pos, p_num)
        await callback_query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    @userge.bot.on_callback_query(filters.regex(pattern=r"back\((.+)\)"))
    @check_owner
    async def callback_back(callback_query: CallbackQuery):
        cur_pos = str(callback_query.matches[0].group(1))
        pos_list = cur_pos.split("|")
        if len(pos_list) == 1:
            await callback_query.answer("Você está no menu principal", show_alert=True)
            return
        if len(pos_list) == 2:
            text = " 🍎 AppleBot 𝐌𝐄𝐍𝐔 "
            buttons = main_menu_buttons()
        elif len(pos_list) == 3:
            text, buttons = category_data(cur_pos)
        elif len(pos_list) == 4:
            text, buttons = plugin_data(cur_pos)
        await callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(buttons)
        )

    @userge.bot.on_callback_query(filters.regex(pattern=r"enter\((.+)\)"))
    @check_owner
    async def callback_enter(callback_query: CallbackQuery):
        cur_pos = str(callback_query.matches[0].group(1))
        pos_list = cur_pos.split("|")
        if len(pos_list) == 2:
            text, buttons = category_data(cur_pos)
        elif len(pos_list) == 3:
            text, buttons = plugin_data(cur_pos)
        elif len(pos_list) == 4:
            text, buttons = filter_data(cur_pos)
        await callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(buttons)
        )

    @userge.bot.on_callback_query(
        filters.regex(pattern=r"((?:un)?load|(?:en|dis)able)\((.+)\)")
    )
    @check_owner
    async def callback_manage(callback_query: CallbackQuery):
        task = str(callback_query.matches[0].group(1))
        cur_pos = str(callback_query.matches[0].group(2))
        pos_list = cur_pos.split("|")
        if len(pos_list) == 4:
            if is_filter(pos_list[-1]):
                flt = userge.manager.filters[pos_list[-1]]
            else:
                flt = userge.manager.commands[pos_list[-1]]
            await getattr(flt, task)()
            text, buttons = filter_data(cur_pos)
        else:
            plg = userge.manager.plugins[pos_list[-1]]
            await getattr(plg, task)()
            text, buttons = plugin_data(cur_pos)
        await callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(buttons)
        )

    @userge.bot.on_callback_query(filters.regex(pattern=r"^mm$"))
    @check_owner
    async def callback_mm(callback_query: CallbackQuery):
        await callback_query.edit_message_text(
            " 🍎 AppleBot 𝐌𝐄𝐍𝐔 ",
            reply_markup=InlineKeyboardMarkup(main_menu_buttons()),
        )

    @userge.bot.on_callback_query(filters.regex(pattern=r"^chgclnt$"))
    @check_owner
    async def callback_chgclnt(callback_query: CallbackQuery):
        if not RawClient.DUAL_MODE:
            return await callback_query.answer(
                "Você está usando [MODO BOT], não pode alterar o cliente.",
                show_alert=True,
            )
        if Config.USE_USER_FOR_CLIENT_CHECKS:
            Config.USE_USER_FOR_CLIENT_CHECKS = False
        elif RawClient.DUAL_MODE:
            Config.USE_USER_FOR_CLIENT_CHECKS = True
        await SAVED_SETTINGS.update_one(
            {"_id": "CURRENT_CLIENT"},
            {"$set": {"is_user": Config.USE_USER_FOR_CLIENT_CHECKS}},
            upsert=True,
        )
        await callback_query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(main_menu_buttons())
        )

    @userge.bot.on_callback_query(filters.regex(pattern=r"refresh\((.+)\)"))
    @check_owner
    async def callback_exit(callback_query: CallbackQuery):
        cur_pos = str(callback_query.matches[0].group(1))
        pos_list = cur_pos.split("|")
        if len(pos_list) == 4:
            text, buttons = filter_data(cur_pos)
        else:
            text, buttons = plugin_data(cur_pos)
        await callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(buttons)
        )

    def is_filter(name: str) -> bool:
        split_ = name.split(".")
        return bool(split_[0] and len(split_) == 2)

    def parse_buttons(
        page_num: int,
        cur_pos: str,
        func: Callable[[str], str],
        data: Union[List[str], Dict[str, Any]],
        rows: int = 5,
    ):
        buttons = [
            InlineKeyboardButton(
                func(x), callback_data=f"enter({cur_pos}|{x})".encode()
            )
            for x in sorted(data)
        ]
        pairs = list(map(list, zip(buttons[::2], buttons[1::2])))
        if len(buttons) % 2 == 1:
            pairs.append([buttons[-1]])
        max_pages = ceil(len(pairs) / rows)
        current_page = page_num % max_pages
        if len(pairs) > rows:
            pairs = pairs[current_page * rows : (current_page + 1) * rows] + [
                [
                    InlineKeyboardButton(
                        "« Anterior",
                        callback_data=f"({cur_pos})prev({current_page})".encode(),
                    ),
                    InlineKeyboardButton(
                        "Próximo »",
                        callback_data=f"({cur_pos})next({current_page})".encode(),
                    ),
                ],
            ]
        pairs += default_buttons(cur_pos)
        return pairs

    def main_menu_buttons():
        return parse_buttons(
            0,
            "mm",
            lambda x: f"{_CATEGORY.get(x, '📁')} {x}",
            userge.manager.get_all_plugins(),
        )

    def default_buttons(cur_pos: str):
        tmp_btns = []
        if cur_pos != "mm":
            tmp_btns.append(
                InlineKeyboardButton(
                    "« Voltar", callback_data=f"back({cur_pos})".encode()
                )
            )
            if len(cur_pos.split("|")) > 2:
                tmp_btns.append(InlineKeyboardButton("🌐 Início", callback_data="mm"))
                tmp_btns.append(
                    InlineKeyboardButton(
                        "🔄 Atualizar", callback_data=f"refresh({cur_pos})".encode()
                    )
                )
        else:
            cur_clnt = "🍏" if Config.USE_USER_FOR_CLIENT_CHECKS else "👤 AppleUser"
            tmp_btns.append(
                InlineKeyboardButton(
                    f"🏷 ativo: {cur_clnt}",
                    callback_data="chgclnt",
                )
            )
        return [tmp_btns]

    def category_data(cur_pos: str):
        pos_list = cur_pos.split("|")
        plugins = userge.manager.get_all_plugins()[pos_list[1]]
        text = (
            f"**(`{len(plugins)}`) Plugins em: "
            f"`{_CATEGORY.get(pos_list[1], '📁')} {pos_list[1]}`  Categoria**"
        )
        buttons = parse_buttons(0, "|".join(pos_list[:2]), lambda x: f"▫️ {x}", plugins)
        return text, buttons

    def plugin_data(cur_pos: str, p_num: int = 0):
        pos_list = cur_pos.split("|")
        plg = userge.manager.plugins[pos_list[2]]
        text = f"""📁 <b>Plugin Status<b>

▫️ **Categoria**: `{pos_list[1]}`
▫️ **Nome**: `{plg.name}`
▫️ **Doc**: `{plg.doc}`
▫️ **Comandos**: `{len(plg.commands)}`
▫️ **Filtros**: `{len(plg.filters)}`
▫️ **Carregado**: `{plg.is_loaded}`
▫️ **Ativo**: `{plg.is_enabled}`
"""
        tmp_btns = []
        if plg.is_loaded:
            tmp_btns.append(
                InlineKeyboardButton(
                    "❎ Descarregar",
                    callback_data=f"unload({'|'.join(pos_list[:3])})".encode(),
                )
            )
        else:
            tmp_btns.append(
                InlineKeyboardButton(
                    "✅ Carregar",
                    callback_data=f"load({'|'.join(pos_list[:3])})".encode(),
                )
            )
        if plg.is_enabled:
            tmp_btns.append(
                InlineKeyboardButton(
                    "❎ Desativar",
                    callback_data=f"disable({'|'.join(pos_list[:3])})".encode(),
                )
            )
        else:
            tmp_btns.append(
                InlineKeyboardButton(
                    "✅ Ativar",
                    callback_data=f"enable({'|'.join(pos_list[:3])})".encode(),
                )
            )
        buttons = parse_buttons(
            p_num,
            "|".join(pos_list[:3]),
            lambda x: f"▫️ {x}" if is_filter(x) else f" {x}",
            (flt.name for flt in plg.commands + plg.filters),
        )
        buttons = buttons[:-1] + [tmp_btns] + [buttons[-1]]
        return text, buttons

    def filter_data(cur_pos: str):
        pos_list = cur_pos.split("|")
        plg = userge.manager.plugins[pos_list[2]]
        flts = {flt.name: flt for flt in plg.commands + plg.filters}
        flt = flts[pos_list[-1]]
        flt_data = f"""
▫️ **Nome**: `{flt.name}`
▫️ **Doc**: `{flt.doc}`
▫️ **Via Bot**: `{flt.allow_via_bot}`
▫️ **Carregado**: `{flt.is_loaded}`
▫️ **Ativo**: `{flt.is_enabled}`"""
        if hasattr(flt, "about"):
            text = f"""<b><u>Status dos Comandos</u></b>
{flt_data}
{flt.about}
"""
        else:
            text = f"""▫️ <b>Status dos Filtros</b>
{flt_data}
"""
        buttons = default_buttons(cur_pos)
        tmp_btns = []
        if flt.is_loaded:
            tmp_btns.append(
                InlineKeyboardButton(
                    "❎ Descarregar", callback_data=f"unload({cur_pos})".encode()
                )
            )
        else:
            tmp_btns.append(
                InlineKeyboardButton(
                    "✅ Carregar", callback_data=f"load({cur_pos})".encode()
                )
            )
        if flt.is_enabled:
            tmp_btns.append(
                InlineKeyboardButton(
                    "❎ Desativar", callback_data=f"disable({cur_pos})".encode()
                )
            )
        else:
            tmp_btns.append(
                InlineKeyboardButton(
                    "✅ Ativar", callback_data=f"enable({cur_pos})".encode()
                )
            )
        buttons = [tmp_btns] + buttons
        return text, buttons

    @userge.bot.on_inline_query()
    async def inline_answer(_, inline_query: InlineQuery):
        results = []
        i_q = inline_query.query
        string = i_q.lower()  # All lower
        str_x = i_q.split(" ", 2)  # trigger @username Text
        str_y = i_q.split(" ", 1)  # trigger and Text
        string_split = string.split()  # All lower and Split each word
        iq_user_id = inline_query.from_user.id
        if (
            (iq_user_id in Config.OWNER_ID)
            or (iq_user_id in Config.SUDO_USERS)
            and Config.SUDO_ENABLED
        ):
            if string == "_check_":
                fyfy = [
                    [
                        InlineKeyboardButton(
                            text="⚡️ 𝐏𝐑𝐄𝐌𝐈𝐔𝐌", callback_data="status_apple"
                        ),
                    ],
                ]
                results.append(
                    InlineQueryResultPhoto(
                        caption=_check_.apple(),
                        reply_markup=_check_.check_buttons(),
                    )
                )

            if string == "age_verification_alert":
                buttons = [
                    [
                        InlineKeyboardButton(
                            text="Yes I'm 18+", callback_data="age_verification_true"
                        ),
                        InlineKeyboardButton(
                            text="No I'm Not", callback_data="age_verification_false"
                        ),
                    ]
                ]
                results.append(
                    InlineQueryResultPhoto(
                        photo_url="https://i.imgur.com/Zg58iXc.jpg",
                        caption="**ARE YOU OLD ENOUGH FOR THIS ?**",
                        reply_markup=InlineKeyboardMarkup(buttons),
                    )
                )

                # COMEÇO
            if string == "afk_mensagem":
                buttons = [
                    [
                        InlineKeyboardButton(
                            text="⚡️ STATUS", callback_data="status_afk"
                        ),
                        InlineKeyboardButton(text="+", callback_data="afk_pm_"),
                    ]
                ]
                results.append(
                    InlineQueryResultPhoto(
                        photo_url="https://telegra.ph/file/511bd5c471bddfd6839d6.jpg",
                        caption=f"{random.choice(CONTATO)}",
                        reply_markup=InlineKeyboardMarkup(buttons),
                    )
                )
                # FIM

            if str_y[0] == "reddit":
                reddit_api = "https://meme-api.herokuapp.com/gimme/"
                if len(str_y) == 2:
                    subreddit_regex = r"^([a-zA-Z]+)\.$"
                    match = re.search(subreddit_regex, str_y[1])
                    if match:
                        subreddit_name = match.group(1)
                        reddit_api += f"{subreddit_name}/30"
                    else:
                        return
                else:
                    reddit_api += "30"
                try:
                    r = await get_response.json(reddit_api)
                except ValueError:
                    results.append(
                        InlineQueryResultArticle(
                            title="Reddit Api is Down !",
                            input_message_content=InputTextMessageContent(
                                "**Error Code: Status != 200**"
                            ),
                            thumb_url="https://i.imgur.com/7a7aPVa.png",
                        )
                    )
                else:
                    if "code" in r:
                        bool_is_gallery = False
                        code = r["code"]
                        code_message = r["message"]
                        results.append(
                            InlineQueryResultArticle(
                                title=str(code),
                                input_message_content=InputTextMessageContent(
                                    f"**Error Code: {code}**\n`{code_message}`"
                                ),
                                description="Enter A Valid Subreddit Name !",
                                thumb_url="https://i.imgur.com/7a7aPVa.png",
                            )
                        )
                    else:
                        bool_is_gallery = True
                        for post in r["memes"]:
                            if "url" in post:
                                postlink = post["postLink"]
                                subreddit = post["subreddit"]
                                title = post["title"]
                                media_url = post["url"]
                                author = post["author"]
                                upvote = post["ups"]
                                captionx = f"<b>{title}</b>\n"
                                captionx += f"`Posted by u/{author}`\n"
                                captionx += f"↕️ <code>{upvote}</code>\n"
                                thumbnail = reddit_thumb_link(post["preview"])
                                if post["spoiler"]:
                                    captionx += "⚠️ Post marked as SPOILER\n"
                                if post["nsfw"]:
                                    captionx += "🔞 Post marked Adult \n"
                                buttons = [
                                    [
                                        InlineKeyboardButton(
                                            f"Source: r/{subreddit}", url=postlink
                                        )
                                    ]
                                ]
                                if media_url.endswith(".gif"):
                                    results.append(
                                        InlineQueryResultAnimation(
                                            animation_url=media_url,
                                            thumb_url=thumbnail,
                                            caption=captionx,
                                            reply_markup=InlineKeyboardMarkup(buttons),
                                        )
                                    )
                                else:
                                    results.append(
                                        InlineQueryResultPhoto(
                                            photo_url=media_url,
                                            thumb_url=thumbnail,
                                            caption=captionx,
                                            reply_markup=InlineKeyboardMarkup(buttons),
                                        )
                                    )
                    await inline_query.answer(
                        results=results,
                        cache_time=1,
                        is_gallery=bool_is_gallery,
                        switch_pm_text="Available Commands",
                        switch_pm_parameter="inline",
                    )
                    return
                # COMEÇO
            if string == "inline_info_afk":
                buttons = [
                    [
                        InlineKeyboardButton(text="+", callback_data="afk_extra"),
                    ]
                ]
                results.append(
                    InlineQueryResultPhoto(
                        photo_url="https://telegra.ph/file/74e96eb1e818131c4440b.png",
                        caption="**Clique no botão para carregar**",
                        reply_markup=InlineKeyboardMarkup(buttons),
                    )
                )
                # FIM
            if string == "alive":
                alive_info = Bot_Alive.alive_info()
                buttons = Bot_Alive.alive_buttons()
                if not Config.ALIVE_MEDIA:
                    results.append(
                        InlineQueryResultPhoto(
                            photo_url=Bot_Alive.alive_default_imgs(),
                            caption=alive_info,
                            reply_markup=buttons,
                        )
                    )
                else:
                    if Config.ALIVE_MEDIA.lower().strip() == "false":
                        results.append(
                            InlineQueryResultArticle(
                                title="@applled",
                                input_message_content=InputTextMessageContent(
                                    alive_info, disable_web_page_preview=True
                                ),
                                description="Envie o Check",
                                reply_markup=buttons,
                            )
                        )
                    else:
                        _media_type, _media_url = await Bot_Alive.check_media_link(
                            Config.ALIVE_MEDIA
                        )
                        if _media_type == "url_gif":
                            results.append(
                                InlineQueryResultAnimation(
                                    animation_url=_media_url,
                                    caption=alive_info,
                                    reply_markup=buttons,
                                )
                            )
                        elif _media_type == "url_image":
                            results.append(
                                InlineQueryResultPhoto(
                                    photo_url=_media_url,
                                    caption=alive_info,
                                    reply_markup=buttons,
                                )
                            )
                        elif _media_type == "tg_media":
                            c_file_id = Bot_Alive.get_bot_cached_fid()
                            if c_file_id is None:
                                try:
                                    c_file_id = get_file_id(
                                        await userge.bot.get_messages(
                                            _media_url[0], _media_url[1]
                                        )
                                    )
                                except Exception as b_rr:
                                    await CHANNEL.log(str(b_rr))
                            if Bot_Alive.is_photo(c_file_id):
                                results.append(
                                    InlineQueryResultCachedPhoto(
                                        file_id=c_file_id,
                                        caption=alive_info,
                                        reply_markup=buttons,
                                    )
                                )
                            else:
                                results.append(
                                    InlineQueryResultCachedDocument(
                                        title="Check @applled",
                                        file_id=c_file_id,
                                        caption=alive_info,
                                        description="Bot Online",
                                        reply_markup=buttons,
                                    )
                                )

            # String para o móudlo AFK - COMEÇO

            if string == "afk":
                results.append(
                    InlineQueryResultAnimation(
                        animation_url=_afk_.link(),
                        caption=_afk_.out_str(),
                        reply_markup=_afk_.afk_buttons(),
                    )
                )

            if string == "afk_":
                results.append(
                    InlineQueryResultPhoto(
                        photo_url=_afk_.link(),
                        caption=_afk_.out_str(),
                        reply_markup=_afk_.afk_buttons(),
                    )
                )

            if string == "_afk_":
                results.append(
                    InlineQueryResultArticle(
                        title="AFK AppleBot",
                        input_message_content=InputTextMessageContent(_afk_._out_str()),
                        reply_markup=_afk_.afk_buttons(),
                    )
                )

            # String para o móudlo AFK - FIM

            if string == "geass":
                results.append(
                    InlineQueryResultAnimation(
                        animation_url="https://i.imgur.com/DeZHcRK.gif",
                        caption="To defeat evil, I must become a greater evil",
                    )
                )

            if str_y[0] == "inotes" and len(str_y) == 2:
                note_data = str_y[1].split("_", 2)
                note_data = [int(x) for x in note_data]
                if len(note_data) == 3:
                    cnote = await get_inote(
                        note_id=note_data[0], chat_id=note_data[1], user_id=note_data[2]
                    )
                    type_ = cnote.get("type")
                    if type_ == "image":
                        results.append(
                            InlineQueryResultCachedPhoto(
                                file_id=cnote.get("file_id"),
                                caption=cnote.get("caption"),
                                reply_markup=cnote.get("buttons"),
                            )
                        )
                    elif type_ == "media":
                        results.append(
                            InlineQueryResultCachedDocument(
                                title="Inline Note",
                                file_id=cnote.get("file_id"),
                                caption=cnote.get("caption"),
                                description=f"#{note_data[0]}",
                                reply_markup=cnote.get("buttons"),
                            )
                        )
                    else:
                        results.append(
                            InlineQueryResultArticle(
                                title="Inline Note",
                                input_message_content=InputTextMessageContent(
                                    cnote.get("caption"), disable_web_page_preview=True
                                ),
                                description=f"#{note_data[0]}",
                                reply_markup=cnote.get("buttons"),
                            )
                        )

            if string == "gapps":
                buttons = [
                    [
                        InlineKeyboardButton("Open GApps", callback_data="open_gapps"),
                        InlineKeyboardButton(
                            "Flame GApps", callback_data="flame_gapps"
                        ),
                    ],
                    [InlineKeyboardButton("Nik GApps", callback_data="nik_gapps")],
                ]
                results.append(
                    InlineQueryResultArticle(
                        title="gapps",
                        input_message_content=InputTextMessageContent(
                            "[\u200c](https://telegra.ph/file/3c4911c20428bd25c8d2e.gif) **Gapps Módulo**"
                        ),
                        description="Módulo teste para o @applled",
                        thumb_url="https://telegra.ph/file/d432a65c7cfbef904c4b3.gif",
                        reply_markup=InlineKeyboardMarkup(buttons),
                    )
                )
            if string == "menu":
                buttons = [
                    [
                        InlineKeyboardButton("Open GApps", callback_data="open_gapps"),
                        InlineKeyboardButton(
                            "Flame GApps", callback_data="flame_gapps"
                        ),
                    ],
                    [InlineKeyboardButton("Nik GApps", callback_data="nik_gapps")],
                ]
                results.append(
                    InlineQueryResultArticle(
                        title="menu",
                        input_message_content=InputTextMessageContent(
                            "[\u200c](https://telegra.ph/file/3c4911c20428bd25c8d2e.gif) **Módulo teste**"
                        ),
                        description="Módulo teste para o @applled",
                        thumb_url="https://telegra.ph/file/d432a65c7cfbef904c4b3.gif",
                        reply_markup=InlineKeyboardMarkup(buttons),
                    )
                )

            if len(string_split) == 2 and (string_split[0] == "ofox"):
                codename = string_split[1]
                t = TelegraphPoster(use_api=True)
                t.create_api_token("Orange")
                photo = "https://i.imgur.com/582uaSk.png"
                api_host = "https://api.orangefox.download/v2/device/"
                try:
                    async with get_response.get_session() as session:
                        r = await get_response.json(
                            f"{api_host}{codename}", session=session
                        )
                        s = await get_response.json(
                            f"{api_host}{codename}/releases/stable/last",
                            session=session,
                        )
                except ValueError:
                    return
                info = f"📱 **Device**: {r['fullname']}\n"
                info += f"👤 **Maintainer**: {r['maintainer']['name']}\n\n"
                recovery = f"🦊 <code>{s['file_name']}</code>\n"
                recovery += f"📅 {s['date']}\n"
                recovery += f"ℹ️ **Version:** {s['version']}\n"
                recovery += f"📌 **Build Type:** {s['build_type']}\n"
                recovery += f"🔰 **Size:** {s['size_human']}\n\n"
                recovery += "📍 **Changelog:**\n"
                recovery += f"<code>{s['changelog']}</code>\n\n"
                msg = info
                msg += recovery
                notes_ = s.get("notes")
                if notes_:
                    notes = t.post(title="READ Notes", author="", text=notes_)
                    buttons = [
                        [
                            InlineKeyboardButton("🗒️ NOTES", url=notes["url"]),
                            InlineKeyboardButton("⬇️ DOWNLOAD", url=s["url"]),
                        ]
                    ]
                else:
                    buttons = [[InlineKeyboardButton(text="⬇️ DOWNLOAD", url=s["url"])]]
                results.append(
                    InlineQueryResultPhoto(
                        photo_url=photo,
                        thumb_url="https://i.imgur.com/o0onLYB.jpg",
                        title="Latest OFOX RECOVERY",
                        description=f"For device : {codename}",
                        caption=msg,
                        reply_markup=InlineKeyboardMarkup(buttons),
                    )
                )

            if string == "repo":
                results.append(REPO_X)

            if len(str_y) == 2 and str_y[0] == "anime":
                for i in await Anime.search(str_y[1]):
                    results.append(
                        InlineQueryResultArticle(
                            title=i.get("title"),
                            input_message_content=InputTextMessageContent(
                                f'[\u200c]({i.get("image")})**{i.get("title")}**\n{i.get("release")}'
                            ),
                            description=i.get("release"),
                            thumb_url=i.get("image"),
                            reply_markup=InlineKeyboardMarkup(
                                [
                                    [
                                        InlineKeyboardButton(
                                            text="⬇️  Download",
                                            callback_data=f'get_eps{i.get("key")}',
                                        )
                                    ]
                                ]
                            ),
                        )
                    )
                if len(results) != 0:
                    await inline_query.answer(
                        results=results[:50],
                        cache_time=1,
                        switch_pm_text="Available Commands",
                        switch_pm_parameter="inline",
                    )
                    return
            # COMEÇO
            if str_y[0] == "spoiler":
                if not os.path.exists(f"{Config.CACHE_PATH}/spoiler_db.json"):
                    results.append(
                        InlineQueryResultArticle(
                            title="No Spoiler Found",
                            input_message_content=InputTextMessageContent(
                                "No Spoiler Found !\nLet's Add Some 😈"
                            ),
                            description="See .help spoiler for more info",
                        )
                    )
                else:
                    bot_name = (await userge.bot.get_me()).username
                    if len(str_y) == 2:
                        link = f"https://t.me/{bot_name}?start=spoiler_{str_y[1]}"
                        buttons = [
                            [InlineKeyboardButton(text="View Spoiler", url=link)]
                        ]
                        results.append(
                            InlineQueryResultArticle(
                                title="Spoiler",
                                input_message_content=InputTextMessageContent(
                                    "<b>Click To View The Spoiler !</b>"
                                ),
                                description="Click To Send",
                                thumb_url="https://telegra.ph/file/ee3a6439494463acd1a3a.jpg",
                                reply_markup=InlineKeyboardMarkup(buttons),
                            )
                        )
                    else:
                        fo = open(f"{Config.CACHE_PATH}/spoiler_db.json")
                        view_db = ujson.load(fo)
                        fo.close()
                        if len(view_db) != 0:
                            for numm, spoilerr in enumerate(view_db, start=1):
                                buttons = [
                                    [
                                        InlineKeyboardButton(
                                            text="View Spoiler",
                                            url=f"https://t.me/{bot_name}?start=spoiler_{spoilerr}",
                                        )
                                    ]
                                ]
                                saved_at = view_db.get(spoilerr, None)
                                savetime = (
                                    saved_at.get("savetime", None) if saved_at else None
                                )
                                results.append(
                                    InlineQueryResultArticle(
                                        title=f"#{numm}  Spoiler",
                                        input_message_content=InputTextMessageContent(
                                            "<b>Click To View The Spoiler !</b>"
                                        ),
                                        description=f"Created At: {savetime}",
                                        thumb_url="https://telegra.ph/file/ee3a6439494463acd1a3a.jpg",
                                        reply_markup=InlineKeyboardMarkup(buttons),
                                    )
                                )
            # FIM
            if str_x[0].lower() == "op" and len(str_x) > 1:
                txt = i_q[3:]
                opinion = os.path.join(Config.CACHE_PATH, "emoji_data.txt")
                if os.path.exists(opinion):
                    with open(opinion) as fo:
                        view_data = ujson.load(fo)
                    # Uniquely identifies an inline message
                    new_id = {int(inline_query.id): [{}]}
                    view_data.update(new_id)
                else:
                    view_data = {int(inline_query.id): [{}]}
                with open(opinion, "w") as outfile:
                    ujson.dump(view_data, outfile)
                buttons = [
                    [
                        InlineKeyboardButton(
                            "👍", callback_data=f"op_y_{inline_query.id}"
                        ),
                        InlineKeyboardButton(
                            "👎", callback_data=f"op_n_{inline_query.id}"
                        ),
                    ]
                ]
                results.append(
                    InlineQueryResultArticle(
                        title="Ask For Opinion",
                        input_message_content=InputTextMessageContent(txt),
                        description=f"Q. {txt}",
                        thumb_url="https://i.imgur.com/Zlc98qS.jpg",
                        reply_markup=InlineKeyboardMarkup(buttons),
                    )
                )

            if "btn_" in str_y[0] or str_y[0] == "btn":
                inline_db_path = f"{Config.CACHE_PATH}/inline_db.json"
                if os.path.exists(inline_db_path):
                    with open(inline_db_path, "r") as data_file:
                        view_db = ujson.load(data_file)
                    data_count_n = 1
                    reverse_list = list(view_db)
                    reverse_list.reverse()
                    for butt_ons in reverse_list:
                        if data_count_n > 30:
                            view_db.pop(butt_ons, None)
                        data_count_n += 1
                    with open(inline_db_path, "w") as data_file:
                        ujson.dump(view_db, data_file)
                    if str_y[0] == "btn":
                        inline_storage = list(view_db)
                    else:
                        rnd_id = (str_y[0].split("_", 1))[1]
                        inline_storage = [rnd_id]
                    if len(inline_storage) == 0:
                        return
                    for inline_content in inline_storage:
                        inline_db = view_db.get(inline_content)
                        if inline_db:
                            if (
                                inline_db["media_valid"]
                                and int(inline_db["media_id"]) != 0
                            ):
                                saved_msg = await userge.bot.get_messages(
                                    Config.LOG_CHANNEL_ID, int(inline_db["media_id"])
                                )
                                media_data = get_file_id(saved_msg)
                            textx, buttonsx = pb(inline_db["msg_content"])
                            if inline_db["media_valid"]:
                                if saved_msg.photo:
                                    results.append(
                                        InlineQueryResultCachedPhoto(
                                            file_id=media_data,
                                            caption=textx,
                                            reply_markup=buttonsx,
                                        )
                                    )
                                else:
                                    results.append(
                                        InlineQueryResultCachedDocument(
                                            title=textx,
                                            file_id=media_data,
                                            caption=textx,
                                            description="Inline Button",
                                            reply_markup=buttonsx,
                                        )
                                    )
                            else:
                                results.append(
                                    InlineQueryResultArticle(
                                        title=textx,
                                        input_message_content=InputTextMessageContent(
                                            textx
                                        ),
                                        reply_markup=buttonsx,
                                    )
                                )

            if str_y[0].lower() == "stylish" and len(str_y) == 2:
                results = []
                for f_name in Styled.font_choice:
                    styled_str = font_gen(f_name, str_y[1])
                    results.append(
                        InlineQueryResultArticle(
                            title=f_name.upper(),
                            input_message_content=InputTextMessageContent(
                                f"`{styled_str}`"
                            ),
                            description=styled_str,
                        )
                    )
                await inline_query.answer(
                    results=results,
                    cache_time=1,
                    switch_pm_text="Available Commands",
                    switch_pm_parameter="inline",
                )
                return

            if str_x[0].lower() in ["secret", "troll"] and len(str_x) == 3:
                user_name = str_x[1]
                msg = str_x[2]
                try:
                    receiver = await userge.get_users(user_name)
                except (BadRequest, IndexError):
                    return
                secret = os.path.join(Config.CACHE_PATH, "secret.json")
                key_ = rand_key()
                r_name = (
                    ("@" + receiver.username)
                    if receiver.username
                    else f"{receiver.first_name} {receiver.last_name or ''}"
                )
                secret_data = {
                    key_: {
                        "sender": iq_user_id,
                        "receiver": {"id": receiver.id, "name": r_name},
                        "msg": msg,
                        "views": [],
                    }
                }
                if os.path.exists(secret):
                    with open(secret) as outfile:
                        view_data = ujson.load(outfile)
                    view_data.update(secret_data)
                else:
                    view_data = secret_data
                # Save
                with open(secret, "w") as r:
                    ujson.dump(view_data, r, indent=4)
                if str_x[0].lower() == "secret":
                    c_data = f"secret_{key_}"
                    i_m_content = f"📩 <b>Secret Msg</b> for <b>{r_name}</b>. Only he/she can open it."
                    i_l_des = f"Send Secret Message to: {r_name}"
                    title = "Send A Secret Message"
                    thumb_img = "https://i.imgur.com/c5pZebC.png"
                else:
                    c_data = f"troll_{key_}"
                    i_m_content = f"😈 Only <b>{r_name}</b> can't view this message. UwU"
                    i_l_des = f"Message Hidden from {r_name}"
                    title = "😈 Troll"
                    thumb_img = "https://i.imgur.com/0vg5B0A.png"
                buttons = [[InlineKeyboardButton("🔐  SHOW", callback_data=c_data)]]
                results.append(
                    InlineQueryResultArticle(
                        title=title,
                        input_message_content=InputTextMessageContent(i_m_content),
                        description=i_l_des,
                        thumb_url=thumb_img,
                        reply_markup=InlineKeyboardMarkup(buttons),
                    )
                )

            if str_y[0].lower() == "ytdl" and len(str_y) == 2:
                link = get_yt_video_id(str_y[1].strip())
                found_ = True
                if link is None:
                    search = VideosSearch(str_y[1].strip(), limit=15)
                    resp = (search.result()).get("result")
                    if len(resp) == 0:
                        found_ = False
                    else:
                        outdata = await result_formatter(resp)
                        key_ = rand_key()
                        ytsearch_data.store_(key_, outdata)
                        buttons = InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        text=f"1 / {len(outdata)}",
                                        callback_data=f"ytdl_next_{key_}_1",
                                    )
                                ],
                                [
                                    InlineKeyboardButton(
                                        text="📜  List all",
                                        callback_data=f"ytdl_listall_{key_}_1",
                                    ),
                                    InlineKeyboardButton(
                                        text="⬇️  Download",
                                        callback_data=f'ytdl_download_{outdata[1]["video_id"]}_0',
                                    ),
                                ],
                            ]
                        )
                        caption = outdata[1]["message"]
                        photo = outdata[1]["thumb"]
                else:
                    caption, buttons = await download_button(link, body=True)
                    photo = await get_ytthumb(link)

                if found_:
                    results.append(
                        InlineQueryResultPhoto(
                            photo_url=photo,
                            title=link,
                            description="⬇️ Click to Download",
                            caption=caption,
                            reply_markup=buttons,
                        )
                    )
                else:
                    results.append(
                        InlineQueryResultArticle(
                            title="not Found",
                            input_message_content=InputTextMessageContent(
                                f"No Results found for `{str_y[1]}`"
                            ),
                            description="INVALID",
                        )
                    )

            MAIN_MENU = InlineQueryResultArticle(
                title="Menu Principal",
                input_message_content=InputTextMessageContent(
                    " Bem vindo ao\n AppleBot 𝐌𝐄𝐍𝐔 "
                ),
                url="https://t.me/applled",
                description="Menu Principal",
                thumb_url="https://telegra.ph/file/c253bbfab1a1a2e79cd9b.png",
                reply_markup=InlineKeyboardMarkup(main_menu_buttons()),
            )
            results.append(MAIN_MENU)
            if len(results) != 0:
                await inline_query.answer(
                    results=results,
                    cache_time=1,
                    switch_pm_text="Comandos Disponíveis",
                    switch_pm_parameter="inline",
                )
        else:
            results.append(REPO_X)
            owner_name = (await userge.get_me()).first_name
            await inline_query.answer(
                results=results,
                cache_time=1,
                switch_pm_text=f"Bot exclusivo para {owner_name}",
                switch_pm_parameter="start",
            )
