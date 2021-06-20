# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os

import speedtest
import wget

from userge import Message, userge
from userge.utils import humanbytes

CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd("speedtest", about={"header": "Teste a velocidade do servidor"})
async def speedtst(message: Message):
    await message.edit("Iniciando o teste de velocidade...")
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        await message.try_to_edit(
            "Testando conexão..[.](https://telegra.ph/file/7662a65b152e41b79837e.jpg)"
        )
        test.download()
        await message.try_to_edit(
            "Aguarde..[.](https://telegra.ph/file/88f85a63b232f9db1e4ba.jpg)"
        )
        test.upload()
        test.results.share()
        result = test.results.dict()
    except Exception as e:
        await message.err(text=e)
        return
    path = wget.download(result["share"])
    output = f"""**--Resultado do Teste Iniciado em {result['timestamp']}--

Cliente: 🍏 AppleBot

ISP: `{result['client']['isp']}`
País: `{result['client']['country']}`

Servidor: @twapple
➖➖➖➖➖➖
Nome: `{result['server']['name']}`
País: `{result['server']['country']}, {result['server']['cc']}`
Anunciante: `{result['server']['sponsor']}`
Latência: `{result['server']['latency']}`
➖➖➖➖➖➖
Ping: `{result['ping']}`
Enviados: `{humanbytes(result['bytes_sent'])}`
Recebidos: `{humanbytes(result['bytes_received'])}`
Download: `{humanbytes(result['download'] / 8)}/s`
Upload: `{humanbytes(result['upload'] / 8)}/s`**"""
    msg = await message.client.send_photo(
        chat_id=message.chat.id, photo=path, caption=output
    )
    await CHANNEL.fwd_msg(msg)
    os.remove(path)
    await message.delete()
