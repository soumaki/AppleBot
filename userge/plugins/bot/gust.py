""" Módulo de testes para o @applled com fins de aprendizado  """

import random

from pyrogram import filters
from pyrogram.errors import MessageNotModified
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)

from userge import userge
from userge.utils import get_file_id

LOGGER = userge.getLogger(__name__)

CONTATO = (
    "🏷 | 𝐒𝐓𝐀𝐓𝐔𝐒\n ╰• Que curiosidade, né?\n\n<i>Então,\n Você pode entrar em contato comigo diretamentepelo meu bot. Para evitar spam, responderei exclusivamente por ele. Em alguns casos, não terei problemas em enviar mensagens no particular.</i>\n\n🔗 @twapple\n ╰• 𝚁𝚎𝚜𝚎𝚛𝚟𝚊𝚍𝚘 𝚙𝚊𝚛𝚊 𝚙𝚘𝚜𝚝𝚜 𝚊𝚕𝚎𝚊𝚝ó𝚛𝚒𝚘𝚜 𝚍𝚘 @applled",
)


async def afk_pm(msg):
    bot = await userge.bot.get_me()
    x = await userge.get_inline_bot_results(bot.username, "afk_mensagem")
    await msg.delete()
    await userge.send_inline_bot_result(
        chat_id=msg.chat.id, query_id=x.query_id, result_id=x.results[0].id
    )
    return True


if userge.has_bot:
    # Query para resultado do Primeiro Clique + Gerar Mensagem # Início
    @userge.bot.on_callback_query(filters.regex(pattern=r"^alive_pm_$"))
    async def afk_resultado(_, c_q: CallbackQuery):
        c_q.from_user.id  # u_id =
        await c_q.answer("Contato com Apple", show_alert=True)
        msg = await userge.bot.get_messages("xapplebot", 3)
        f_id = get_file_id(msg)
        mensagem = f"{random.choice(CONTATO)}"
        buttons = [
            [
                InlineKeyboardButton(
                    text="❎ Mensagem Privada",
                    url="https://t.me/AssistantAPBot",
                )
            ]
        ]
        try:
            await c_q.edit_message_media(
                media=InputMediaPhoto(media=f_id, caption=mensagem),
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        except MessageNotModified:
            return

    # Query para resultado do Primeiro Clique + Gerar Mensagem # FIM
