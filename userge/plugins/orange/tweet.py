""" Manter os créditos | @applled - Módulo para Tweets ;) """


from pyrogram.errors import YouBlockedUser

from userge import Message, userge
from userge.utils.exceptions import StopConversation


@userge.on_cmd(
    "tweet",
    about={
        "titulo": "Tweet uma mensagem",
        "flags": {"-l": "limite, para várias mensagens"},
        "como usar": "Responda {tr}t -l[limite de mensagem]",
        "exemplo": ["{tr}t", "{tr}t -15"],
    },
    allow_via_bot=False,
    del_pre=True,
)
async def tweetando(message: Message):
    """Tweetando com estilo @applled"""
    reply = message.reply_to_message
    quote_list = []
    self_mid = False
    args = ""
    if reply:
        if "l" in message.flags:
            limit = message.flags.get("l", 1)
            if not limit.isdigit():
                await message.err("Eu preciso de um texto, não de ventos.", del_in=5)
                return
            num_ = min(int(limit), 24)
            async for msg in userge.iter_history(
                message.chat.id, limit=num_, offset_id=reply.message_id, reverse=True
            ):
                if msg.message_id != message.message_id:
                    quote_list.append(msg.message_id)
            if message.filtered_input_str:
                self_mid = True
                await message.edit(message.filtered_input_str)
        else:
            quote_list.append(reply.message_id)
            if message.input_str:
                self_mid = True
                await message.edit(message.input_str)
    else:
        args = message.input_str
    if self_mid:
        quote_list.append(message.message_id)
    else:
        await message.delete()
    if not args and len(quote_list) == 0:
        await message.err("Responda uma mensagem ou faça o comando + texto.", del_in=5)
        return
    try:
        async with userge.conversation("TwitterStatusBot ", timeout=100) as conv:
            try:
                if quote_list:
                    await userge.forward_messages(
                        "TwitterStatusBot ", message.chat.id, quote_list
                    )
                    if self_mid:
                        await message.delete()
                elif args:
                    await conv.send_message(args)
            except YouBlockedUser:
                await message.edit("Dê /start no @TwitterStatusBot ")
                return
            quote = await conv.get_response(mark_read=True)
            if not (quote.sticker or quote.document):
                await message.err("Algo de certo está errado.")
                return
            message_id = reply.message_id if reply else None
            if quote.sticker:
                await userge.send_sticker(
                    chat_id=message.chat.id,
                    sticker=quote.sticker.file_id,
                    reply_to_message_id=message_id,
                )
            else:
                await userge.send_document(
                    chat_id=message.chat.id,
                    document=quote.document.file_id,
                    reply_to_message_id=message_id,
                )
    except StopConversation:
        await message.err(
            "@TwitterStatusBot ficou sem resposta.\nTente novamente.", del_in=5
        )
