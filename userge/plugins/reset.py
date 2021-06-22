import asyncio

from userge import Message, userge

# Applled tools


@userge.on_cmd(
    "reset$", about={"header": "Reiniciar Bot"}, trigger="", allow_via_bot=False
)
async def reset_(message: Message):
    """reset"""
    reset = "!ree -apple"
    await message.try_to_edit(reset, del_in=1)


async def check_and_send(message: Message, *args, **kwargs):
    replied = message.reply_to_message
    if replied:
        await asyncio.gather(message.delete(), replied.reply(*args, **kwargs))
    else:
        await message.edit(*args, **kwargs)
