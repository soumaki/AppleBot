""" @Applled - Lindo e maravilhoso """

from userge import Message, userge


@userge.on_cmd(
    "con$", about={"título": "Tu sabe o que é :D"}, trigger="", allow_via_bot=False
)
async def conquer_msg(message: Message):
    await message.edit(
        "ⓘ <i>Exclusive Message for ConquerOS Premium. Only Private Premium User can view this message.</i> <u>[More Details](https://bit.ly/conquerpremium)</u>",
        disable_web_page_preview=True,
    )
