""" Módulo para gerar fotos de pessoas não reais - Fake | Módulo criado pelo @applled - Manter os créditos """

import asyncio
import random

from userge import Message, userge

RESULTADO = ("https://boredhumans.b-cdn.net/faces2/",)


@userge.on_cmd(
    "fake",
    about={
        "titulo": "Foto de Perfil não real",
        "descrição": "Módulo para gerar fotos de pessoas não reais",
        "como usar": "{tr}fake",
    },
)
async def foto_falsa(message: Message):
    await message.edit(f"<i>Foto Fake | Carregada</i>", del_in=1, log=__name__)
    falso = f"""{random.choice(RESULTADO)}{random.choice(range(0,994))}.jpg"""
    texto = f"**Foto Fake Gerada** ✅\n\n**Criado por:** <i>@iamakima</i>\n<i>Divirta-se ;)</i>"
    await message.client.send_photo(
        message.chat.id,
        photo=falso,
        caption=texto,
    )


async def verifica_envia(message: Message, *args, **kwargs):
    replied = message.reply_to_message
    if replied:
        await asyncio.gather(message.delete(), replied.reply(*args, **kwargs))
    else:
        await message.edit(*args, **kwargs)
