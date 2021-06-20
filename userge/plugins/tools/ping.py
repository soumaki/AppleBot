# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
from datetime import datetime

from userge import Message, userge


@userge.on_cmd(
    "local",
    about={
        "header": "check how long it takes to ping your userbot",
        "flags": {"-a": "average ping"},
    },
    group=-1,
)
async def pingme(message: Message):
    start = datetime.now()
    if "-orange" in message.flags:
        await message.edit("<code> abrindo terminal... </code>")
        await asyncio.sleep(0.5)
        await message.edit("<code> executando comando.. </code>")
        await asyncio.sleep(0.5)
        await message.edit("<code> ▫️ ping local/@laranjudo -t</code>")
        await asyncio.sleep(0.5)
        await message.edit("<code> ping local/@laranjudo -t</code>")
        await asyncio.sleep(0.5)
        await message.edit("<code> ▫️ ping local/@laranjudo -t</code>")
        await asyncio.sleep(0.5)
        await message.edit("<code> ping local/@laranjudo -t</code>")
        end = datetime.now()
        t_m_s = (end - start).microseconds / 1000
        m_s = round((t_m_s - 0.6) / 3, 3)
        await message.edit(
            f"""
**Stats $terminal**
➖➖➖➖➖➖➖
Loaded@: `{m_s} milissegundos`
<code>- local/@laranjudo</code>"""
        )
    else:
        await message.edit("`open terminal...`")
        end = datetime.now()
        m_s = (end - start).microseconds / 1000
        await message.edit(f"**Tudo certo** seu ping: `{m_s} ms ")
