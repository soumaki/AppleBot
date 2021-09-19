import flag as cflag
import humanize
from aiohttp import ClientSession
from datetime import datetime
from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from userge import Message, userge
from userge.utils import post_to_telegraph as post_to_tp
from userge.utils import check_owner

ANIME_TEMPLATE = """{name}
**ID | MAL ID:** `{idm}` | `{idmal}`
◾️ **Original:** `{source}`
◾️ **Exibido em:** `{formats}`{dura}{chrctrsls}
{status_air}
▫️ **Classificação:** `{adult}`
▫️ {trailer_link}
▫️ [Mais detalhes & Sipnospe]({synopsis_link})
{additional}"""

PAGE_QUERY = """
query ($search: String, $pp: Int) {
    Page (perPage: $pp) {
        media (search: $search, type: ANIME) {
            id
            title {
                romaji
                english
            }
            synonyms
        }
    }
}
"""

IANIME_QUERY = """
query ($id: Int, $idMal:Int, $search: String, $type: MediaType, $asHtml: Boolean) {
    Media (id: $id, idMal: $idMal, search: $search, type: $type) {
        id
        idMal
        title {
            romaji
            english
            native
        }
        format
        status
        description (asHtml: $asHtml)
        relations {
            edges {
                node {
                    title {
                        romaji
                        english
                    }
                    id
                }
                relationType
            }
        }
        startDate {
            year
            month
            day
        }
        season
        episodes
        duration
        countryOfOrigin
        source (version: 2)
        trailer {
          id
          site
          thumbnail
        }
        bannerImage
        genres
        averageScore
        nextAiringEpisode {
            airingAt
            timeUntilAiring
            episode
        }
        isAdult
        characters (role: MAIN, page: 1, perPage: 10) {
            nodes {
                id
                name {
                    full
                    native
                }
                image {
                    large
                }
                description (asHtml: $asHtml)
                siteUrl
            }
        }
        studios (isMain: true) {
            nodes {
                name
                siteUrl
            }
        }
        siteUrl
    }
}
"""

async def return_json_senpai(query, vars_):
    """ Makes a Post to https://graphql.anilist.co. """
    url_ = "https://graphql.anilist.co"
    async with ClientSession() as session:
        async with session.post(
            url_, json={"query": query, "variables": vars_}
        ) as post_con:
            json_data = await post_con.json()
    return json_data


def make_it_rw(time_stamp, as_countdown=False):
    """ Converting Time Stamp to Readable Format """
    if as_countdown:
        now = datetime.now()
        air_time = datetime.fromtimestamp(time_stamp)
        return str(humanize.naturaltime(now - air_time))
    return str(humanize.naturaldate(datetime.fromtimestamp(time_stamp)))


@userge.on_cmd(
    "anib",
    about={
        "header": "Advanced Anime Search",
        "description": "Search for Anime using AniList API",
        "usage": "{tr}ianime [anime name]",
        "examples": ["{tr}ianime Asterisk war",]
    },
    allow_private=False
)
async def ianime(message: Message):
    k = await userge.get_me()
    x = await message.reply("`Me conectando ao Anilist...`")
    if x.from_user.id==k.id:
        await x.err("Please verify if bot is present in group")
    query = message.input_str
    get_list = {"search": query, "pp": 20}
    result = await return_json_senpai(PAGE_QUERY, get_list)
    data = result["data"]["Page"]["media"]    
    button = []
    for i in data:
        lstsnnms = " ".join(i['synonyms']) if i['synonyms']!=[] else ""
        eng = i['title']['english'] if i['title']['english']!=None else ""
        rom = i['title']['romaji']
        str_ = f"{rom} {eng} {lstsnnms}".replace(":", "").replace("-", "")
        if query.lower() in str_.lower():
            button.append([InlineKeyboardButton(text=f"{i['title']['romaji']}", callback_data=f"getani_{i['id']}_{query}")])
    buttons = button[:10]
    await message.reply_photo("https://telegra.ph/file/556676e09f8874968b25b.jpg", f'Exibindo os resultados para "{query}":', reply_markup=InlineKeyboardMarkup(buttons))
    await x.delete()

async def ani_info(query_id):
    """ Search Anime Info """
    vars_ = {"id": int(query_id), "asHtml": True, "type": "ANIME"}
    result = await return_json_senpai(IANIME_QUERY, vars_)
    data = result["data"]["Media"]
    # Data of all fields in returned json
    # pylint: disable=possibly-unused-variable
    idm = data.get("id")
    idmal = data.get("idMal")
    romaji = data["title"]["romaji"]
    english = data["title"]["english"]
    native = data["title"]["native"]
    formats = data.get("format")
    status = data.get("status")
    synopsis = data.get("description")
    duration = data.get("duration")
    country = data.get("countryOfOrigin")
    c_flag = cflag.flag(country)
    if data["title"]["english"] is not None:
        name = f'''[{c_flag}]**{romaji}**
        __{english}__
        {native}'''
    else:
        name = f'''[{c_flag}]**{romaji}**
        {native}'''
    source = data.get("source")
    prqlsql = data.get("relations").get('edges')
    prql = ""
    prql_id = ""
    sql = ""
    sql_id = ""
    for i in prqlsql:
        if i['relationType']=="PREQUEL":
            prql += f"**PREQUEL**: `{i['node']['title']['english' or 'romaji']}`\n"
            prql_id += f"{i['node']['id']}"
            break
    for i in prqlsql:
        if i['relationType']=="SEQUEL":
            sql += f"**SEQUEL**: `{i['node']['title']['english' or 'romaji']}`\n"
            sql_id += f"{i['node']['id']}"
            break
    if prql_id=="":
        prql_id += "None"
    if sql_id=="":
        sql_id += "None"
    additional = f"{prql}{sql}"
    bannerImg = data.get("bannerImage")
    dura = f"\n▫️ **Duração:** `{duration} min/ep`" if duration!=None else ""
    charlist = []
    for char in data["characters"]["nodes"]:
        charlist.append(f"    •{char['name']['full']}")
    chrctrs = "\n"
    chrctrs += ("\n").join(charlist[:10])
    chrctrsls = f"\n▫️ **Personagens:** `{chrctrs}`" if len(charlist)!=0 else ""
    air_on = None
    if data["nextAiringEpisode"]:
        nextAir = data["nextAiringEpisode"]["airingAt"]
        air_on = make_it_rw(nextAir)
        ep_ = data['nextAiringEpisode']['episode']
        if ep_=="1":
            th = "st"
        elif ep_=="2":
            th = "nd"
        elif ep_=="3":
            th = "rd"
        else:
            th = "th"
        air_on += f" | {ep_}{th} eps"
    if status=="FINISHED":
        status_air = f"▫️ <b>Status:</b> `{status}`"
    else:
        status_air = f"▫️ <b>Status:</b> `{status}`\n▫️ <b>Próxima exibição:</b> `{air_on}`"
    s_date = data.get("startDate")
    adult = data.get("isAdult")
    trailer_link = "N/A"

    if data["trailer"] and data["trailer"]["site"] == "youtube":
        trailer_link = f"[Trailer](https://youtu.be/{data['trailer']['id']})"
    html_char = ""
    for character in data["characters"]["nodes"]:
        html_ = ""
        html_ += "<br>"
        html_ += f"""<a href="{character['siteUrl']}">"""
        html_ += f"""<img src="{character['image']['large']}"/></a>"""
        html_ += "<br>"
        html_ += f"<h3>{character['name']['full']}</h3>"
        html_ += f"<em>{c_flag} {character['name']['native']}</em><br>"
        html_ += f"<b>ID do personagem</b>: {character['id']}<br>"
        html_ += (
            f"<h4>Sobre o personagem:</h4>{character.get('description', 'N/A')}"
        )
        html_char += f"{html_}<br><br>"

    studios = "".join(
        "<a href='{}'>• {}</a> ".format(studio["siteUrl"], studio["name"])
        for studio in data["studios"]["nodes"]
    )

    url = data.get("siteUrl")

    title_img = f"https://img.anili.st/media/{idm}"
    # Telegraph Post mejik
    html_pc = ""
    html_pc += f"<img src='{title_img}' title={romaji}/>"
    html_pc += f"<h1>[{c_flag}] {native}</h1>"
    html_pc += f"<br><b>Duração:</b> {duration}"
    html_pc += f"<br>{status_air}<br>"
    html_pc += f"<br>{additional}"
    html_pc += "<h3>Sinopse:</h3>"
    html_pc += synopsis
    html_pc += "<br>"
    if html_char:
        html_pc += "<h2>Personagens Principais:</h2>"
        html_pc += html_char
        html_pc += "<br><br>"
    html_pc += "<h3>Mais detalhes:</h3>"
    html_pc += f"<b>Iniciado em:</b> {s_date['day']}/{s_date['month']}/{s_date['year']}"
    html_pc += f"<br><b>Studios:</b> {studios}<br>"
    html_pc += f"<a href='https://myanimelist.net/anime/{idmal}'>Veja em MAL</a>"
    html_pc += f"<a href='{url}'> Vejo no anilist.co</a>"
    html_pc += f"<img src='{bannerImg}'/>"

    title_h = english or romaji
    synopsis_link = post_to_tp(title_h, html_pc)
    finals_ = ANIME_TEMPLATE.format(**locals())
    return title_img, finals_, prql_id, sql_id


@userge.bot.on_callback_query(filters.regex(pattern=r"getani_(.*)"))
@check_owner
async def present_res(cq: CallbackQuery):
    idm = cq.data.split("_")[1]
    query = cq.data.split("_")[2]
    result = await ani_info(idm)
    pic, msg = result[0], result[1]
    btns = []
    if result[2]=="None":
        if result[3]!="None":
            btns.append([InlineKeyboardButton(text="Sequel", callback_data=f"getani_{result[3]}_{query}")])
    else:
        if result[3]!="None":
            btns.append(
                [
                    InlineKeyboardButton(text="Prequel", callback_data=f"getani_{result[2]}_{query}"),
                    InlineKeyboardButton(text="Sequel", callback_data=f"getani_{result[3]}_{query}")
                ]
            )
        else:
            btns.append([InlineKeyboardButton(text="Prequel", callback_data=f"getani_{result[2]}_{query}")])
    btns.append([InlineKeyboardButton(text="Voltar", callback_data=f"back_{query}")])
    await cq.edit_message_media(InputMediaPhoto(pic, caption=msg), reply_markup=InlineKeyboardMarkup(btns))


@userge.bot.on_callback_query(filters.regex(pattern=r"back_(.*)"))
@check_owner
async def present_res(cq: CallbackQuery):
    query = cq.data.split("_")[1]
    get_list = {"search": query, "pp": 10}
    result = await return_json_senpai(PAGE_QUERY, get_list)
    data = result["data"]["Page"]["media"]    
    button = []
    for i in data:
        lstsnnms = " ".join(i['synonyms']) if i['synonyms']!=[] else ""
        eng = i['title']['english'] if i['title']['english']!=None else ""
        rom = i['title']['romaji']
        str_ = f"{rom} {eng} {lstsnnms}"
        if query.lower() in str_.lower():
            button.append([InlineKeyboardButton(text=f"{i['title']['romaji']}", callback_data=f"getani_{i['id']}_{query}")])
    await cq.edit_message_media(InputMediaPhoto("https://telegra.ph/file/556676e09f8874968b25b.jpg", f'{master.first_name}, o resultado de sua pesquisa "{query}":'), reply_markup=InlineKeyboardMarkup(button))
