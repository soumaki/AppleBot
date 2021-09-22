""" @Applled - Lindo e maravilhoso """

from userge import Message, userge


@userge.on_cmd(
    "orange",
    about={
        "header": "Muito fácil usar",
        "usar": "{tr}orange yooo",
    },
)
async def orange_msg(message: Message):
    await message.edit(
        "ⓘ <i>Mensagem Exclusiva para os Administradores. Somente membros com acesso privilegiado podem visualizar esta mensagem.</i> <u>[AppleSecurity](https://bit.ly/applesecuritypremium)</u>",
        disable_web_page_preview=True,
    )
