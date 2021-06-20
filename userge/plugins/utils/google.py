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
        "header": "do a Google search",
        "flags": {
            "-p": "page of results to return (default to 1)",
            "-l": "limit the number of returned results (defaults to 5)(max 10)",
        },
        "usage": "{tr}google [flags] [query | reply to msg]",
        "examples": "{tr}google -p4 -l10 github-userge",
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
        #  output += f"{desc}\n\n"
        except IndexError:
            break
    output = f"""
**Você pesquisou por:**
🔎 `{query}`

**✅ Resultados no Google:**

{output}
➖➖➖➖➖➖
▫️ Dev: @applled
"""
    await message.edit_or_send_as_file(
        text=output, caption=query, disable_web_page_preview=True
    )
