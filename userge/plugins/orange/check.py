""" Módulo de testes para o @applled com fins de aprendizado  """

import random

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from userge import Message, userge

LOGGER = userge.getLogger(__name__)
CHECKS = (
    "https://telegra.ph/file/b2fda41d76cd798d4c368.gif",
    "https://telegra.ph/file/43901682e8a936d76572e.gif",
    "https://telegra.ph/file/140d286c155894093c250.gif",
    "https://telegra.ph/file/ebfb744d7a25736ef09f5.gif",
)


@userge.on_cmd(
    "check",
    about={
        "header": "Módulo teste para o @applled",
    },
    del_pre=True,
    allow_channels=False,
    allow_via_bot=True,
)
async def apple(message: Message):
    await userge.bot.get_me()
    master = await userge.get_me()
    await message.edit(
        "**𝚃𝚎𝚜𝚝𝚎 𝚐𝚎𝚛𝚊𝚍𝚘...**\n𝙰𝚐𝚞𝚊𝚛𝚍𝚎 𝚘 𝚛𝚎𝚜𝚞𝚕𝚝𝚊𝚍𝚘, ;)", del_in=5, log=__name__
    )
    photo = f"""{random.choice(CHECKS)}"""
    texto = f"<u>Estou Online</u>, {master.first_name}"
    await userge.bot.send_animation(
        message.chat.id,
        animation=photo,
        caption=texto,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("+", callback_data="contato_pm"),
                    InlineKeyboardButton("TWAPPLE", url="https://t.me/twapple"),
                ]
            ]
        ),
    )

    # Testar e acrescentar algumas linhas nas hashtags +
