# made for USERGE-X by @Kakashi_HTK(tg)/@ashwinstr(gh) PT-Br/@applled

from pyrogram.errors import YouBlockedUser

from userge import Message, userge


@userge.on_cmd(
    "fstat",
    about={
        "título": "Verifique a Fstat de um usuário",
        "descrição": "Faça uma busca da fstat de um usuário usando a @missrose_bot",
        "como usar": "{tr}fstat [UserID/username] ou [responda uma mensagem com o comando]",
    },
)
async def f_stat(message: Message):
    """Verifique a Fstat de um usuário"""
    reply = message.reply_to_message
    user_ = message.input_str if not reply else reply.from_user.id
    if not user_:
        user_ = message.from_user.id
    try:
        get_u = await userge.get_users(user_)
        user_name = " ".join([get_u.first_name, get_u.last_name or ""])
        user_id = get_u.id
    except BaseException:
        await message.edit(
            f"Buscando informações da FStart do <b>{user_}</b>...\nAVISO: O usuário não foi encontrado em seu banco de dados, Confira o DB na Rose."
        )
        user_name = user_
        user_id = user_
    await message.edit(
        f"Buscando informações da FStart do <a href='tg://user?id={user_id}'><b>{user_name}</b></a>..."
    )
    bot_ = "MissRose_bot"
    async with userge.conversation(bot_, timeout=1000) as conv:
        try:
            await conv.send_message(f"/fstat {user_id}")
        except YouBlockedUser:
            await message.err("Desbloqueie a @missrose_bot primeiro...", del_in=5)
            return
        response = await conv.get_response(mark_read=True)
    fail = "Nunca nem vi."
    resp = response.text
    if fail in resp:
        await message.edit(
            f"Usuário <code>{user_name}</code> não foi encontrado no bando de dados da @MissRose_bot"
        )
    else:
        await message.edit(resp.html, parse_mode="html")
