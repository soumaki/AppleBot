""" @Applled - Lindo e maravilhoso """

from userge import Message, userge


@userge.on_cmd(
    "pro$", about={"título": "Tu sabe o que é :D"}, trigger="", allow_via_bot=False
)
async def proton_msg(message: Message):
    await message.edit(
        "ⓘ <i>Essa mensagem está disponível apenas para usuários da ProtonAOSP Premium.</i> <u>[Saiba mais](https://bit.ly/protonpremium)</u>",
        disable_web_page_preview=True,
    )
