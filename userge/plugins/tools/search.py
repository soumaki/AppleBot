# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

from userge import Message, userge


@userge.on_cmd(
    "s",
    about={"header": "Pesquises comandos no AppleBot", "exemplo": "{tr}s online"},
    allow_channels=False,
)
async def search(message: Message):
    cmd = message.input_str
    if not cmd:
        await message.err(text="Digite qualquer palavra para pesquisar")
        return
    found = [i for i in sorted(list(userge.manager.enabled_commands)) if cmd in i]
    out_str = "    ".join(found)
    if found:
        out = f"**--Eu encontrei ({len(found)}) comandos para sua pesquisa -- : `{cmd}`**\n\n`{out_str}`"
    else:
        out = f"__não encontrei nenhum comando da sua pesquisa__ : `{cmd}`"
    await message.edit(text=out, del_in=0)
