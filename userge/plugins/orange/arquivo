# Teste de Módulo do @Applled para Upload de arquivos #


from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError

from userge import userge


@userge.on_cmd("upar", about={"header": "Teste de plugin"})
# Este módulo é para upar um arquivo no Telegram diretamente de um link #
async def _(event):
    if event.fwd_from:
        return
    if not event.reply_to_msg_id:
        await event.edit("```/// teste 1.```")
        return
    reply_message = await event.get_reply_message()
    if not reply_message.text:
        await event.edit("```/// teste 2.```")
        return
    chat = "@uploadbot"
    sender = reply_message.sender
    if sender.bot:
        await event.edit("```/// teste 3.```")
        return
    await event.edit("```Em processamento, aguarde...```")
    async with event.client.conversation(chat) as conv:
        try:
            response = conv.wait_event(
                events.NewMessage(incoming=True, from_users=830103832)
            )
            await event.client.forward_messages(chat, reply_message)
            response = await response
        except YouBlockedUserError:
            await event.reply("```Desbloqueie o @uploadbot e tente de novo.```")
            return
        if response.text.startswith("Olá,"):
            await event.edit(
                "```você pode desativar suas configurações de privacidade por um momento?```"
            )
        else:
            await event.edit(f"{response.message.message}")
