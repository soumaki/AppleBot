# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

from search_engine_parser.core.engines.google import Search as GoogleSearch

from userge import Message, userge


@userge.on_cmd(
    "google",
    about={
        "header": "Faça uma pesquisa no Google",
        "flags": {
            "-p": "números de páginas para o resultado da pesquisa (o padrão é 1)",
            "-l": "Limite de número dos resultados da pesquisa (padrão está 3)(máximo 10)",
        },
        "como usar": "{tr}google [flags] [pesquisa | responda uma mensagem]",
        "exemplo": "{tr}google -p4 -l10 apple",
    },
)
async def gsearch(message: Message):
    await message.edit("Pesquisando ...")
    query = message.filtered_input_str
    flags = message.flags
    page = int(flags.get("-p", 1))
    limit = int(flags.get("-l", 3))
    if message.reply_to_message:
        query = message.reply_to_message.text
    if not query:
        await message.err(
            text="Forneça um termo ou responda uma mensagem para pesquisar!"
        )
        return
    try:
        g_search = GoogleSearch()
        gresults = await g_search.async_search(query, page)
    except Exception as e:
        await message.err(text=e)
        return
    output = ""
    for i in range(limit):
        try:
            title = gresults["titles"][i]
            link = gresults["links"][i]
            desc = gresults["descriptions"][i]
            output += f"🔗 **[{title}]({link})\n▫️ __{desc}__\n**"
        #           output += f"{desc}\n\n" Ocupa muito espaço
        except IndexError:
            break
    output = f"""
**Você pesquisou por:**
🔎 `{query}`
**✅ Resultados no Google:**
{output}

"""
    await message.edit_or_send_as_file(
        text=output, caption=query, disable_web_page_preview=True
    )
