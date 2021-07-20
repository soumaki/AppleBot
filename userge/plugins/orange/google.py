from search_engine_parser.core.engines.google import Search as GoogleSearch

from userge import Message, userge

LOGGER = userge.getLogger(__name__)


@userge.on_cmd(
    "google",
    about={
        "titulo": "Faça uma pesquisa no Google",
        "flags": {
            "-pag": "números de páginas para o resultado da pesquisa (o padrão é 2)",
            "-lim": "Limite de número dos resultados da pesquisa (padrão está 3)(máximo 10)",
        },
        "como usar": "{tr}google [flags] [pesquisa | responda uma mensagem]",
        "exemplo": "{tr}google -p4 -l10 apple",
    },
    del_pre=True,
    allow_channels=False,
    allow_via_bot=True,
)
async def gsearch(message: Message):
    await message.edit(
        f"**Pesquisa do Google**\n<i>Log Salvo.</i>", del_in=2, log=__name__
    )
    query = message.filtered_input_str
    flags = message.flags
    page = int(flags.get("-pag", 2))
    limit = int(flags.get("-lim", 3))
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
            output += f"🔗 **[{title}]({link})**\n ╰• <i>{desc}</i>\n\n"
        except IndexError:
            break
    output = f"""
𝚂𝚞𝚊 𝚙𝚎𝚜𝚚𝚞𝚒𝚜𝚊 𝚏𝚘𝚒:
🔎 `{query}`

✅ 𝚁𝚎𝚜𝚞𝚕𝚝𝚊𝚍𝚘𝚜:

{output}
🌐 | <code>𝚐𝚘𝚘𝚐𝚕𝚎.𝚌𝚘𝚖</code>
"""
    await message.edit_or_send_as_file(
        text=output,
        caption=query,
        disable_web_page_preview=True,
    )
