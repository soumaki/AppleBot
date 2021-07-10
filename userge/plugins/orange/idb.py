""" Módulo para pesquisa no IMDB @applled """
import os
import re

import bs4
import requests
import wget

from userge import Config, Message, userge

THUMB_PATH = Config.DOWN_PATH + "imdb_thumb.jpg"


@userge.on_cmd(
    "idb",
    about={
        "header": "Obtenha informações sobre qualquer coisa no IMDB",
        "description": "Pesquise informações no IMDB.\n"
        "[NOTA: Para baixar o pôster configure a thumb"
        "o pôster precisa ser no formado imdb_thumb.jpg]",
        "Como usar": "{tr}idb [Nome da pesquisa]",
    },
)
async def imdb(message: Message):
    try:
        movie_name = message.input_str
        await message.edit(f"__Pesquisando no IMDB por__: {movie_name}")
        final_name = movie_name.replace(" ", "+")
        page = requests.get(
            f"https://www.imdb.com/find?ref_=nv_sr_fn&q={final_name}&s=all"
        )
        soup = bs4.BeautifulSoup(page.content, "lxml")
        odds = soup.findAll("tr", "odd")
        mov_title = odds[0].findNext("td").findNext("td").text
        mov_link = (
            "http://www.imdb.com/" + odds[0].findNext("td").findNext("td").a["href"]
        )
        page1 = requests.get(mov_link)
        soup = bs4.BeautifulSoup(page1.content, "lxml")
        image = soup.find("link", attrs={"rel": "image_src"}).get("href", None)
        if soup.find("div", "title_wrapper"):
            pg = soup.find("div", "title_wrapper").findNext("div").text
            mov_details = re.sub(r"\s+", " ", pg)
        else:
            pass
        credits_ = soup.findAll("div", "credit_summary_item")
        director = credits_[0].a.text
        if len(credits_) == 1:
            writer = "Indisponível"
            stars = "Indisponível"
        elif len(credits_) > 2:
            writer = credits_[1].a.text
            actors = [x.text for x in credits_[2].findAll("a")]
            actors.pop()
            stars = actors[0] + "," + actors[1] + "," + actors[2]
        else:
            writer = "Indisponível"
            actors = [x.text for x in credits_[1].findAll("a")]
            actors.pop()
            stars = actors[0] + "," + actors[1] + "," + actors[2]
        if soup.find("div", "inline canwrap"):
            story_line = soup.find("div", "inline canwrap").findAll("p")[0].text
        else:
            pass
        info = soup.findAll("div", "txt-block")
        if info:
            mov_country = []
            mov_language = []
            for node in info:
                a = node.findAll("a")
                for i in a:
                    if "country_of_origin" in i["href"]:
                        mov_country.append(i.text)
                    elif "primary_language" in i["href"]:
                        mov_language.append(i.text)
        if soup.findAll("div", "ratingValue"):
            for r in soup.findAll("div", "ratingValue"):
                mov_rating = r.strong["title"]
        else:
            mov_rating = "Indisponível"
        des_ = f"""

<b>🎬 Título: </b>{mov_title}
➖➖➖➖➖➖➖
<b>Avaliação da audiência:
╰• </b><code>{mov_rating}</code>
<b>Origem: </b><code>{mov_country[0]}</code>
<b>Idioma: </b><code>{mov_language[0]}</code>
➖➖➖➖➖➖➖
<b>INFORMAÇÕES DA PRODUÇÃO</b>
▫️ <b>Diretor:
╰• </b><code>{director}</code>
▫️ <b>Escrito por:
╰• </b><code>{writer}</code>
▫️ <b>Elenco Principal:
╰• </b><code>{stars}</code>
➖➖➖➖➖➖➖

▫️ Mais informações:
🔗 {mov_link}
"""
    except IndexError:
        await message.edit("Poxa, forneça um título que exista! ")
        return
    if os.path.exists(THUMB_PATH):
        if len(des_) > 650:
            des_ = des_[:650] - "..."
        await message.client.send_photo(
            chat_id=message.chat.id, photo=THUMB_PATH, caption=des_, parse_mode="html"
        )
        await message.delete()
    elif image is not None:
        await message.edit("__baixando pôster ...__")
        img_path = wget.download(
            image, os.path.join(Config.DOWN_PATH, "imdb_thumb.jpg")
        )
        if len(des_) > 1024:
            des_ = des_[:650] - "..."
        await message.client.send_photo(
            chat_id=message.chat.id, photo=img_path, caption=des_, parse_mode="html"
        )
        await message.delete()
        os.remove(img_path)
    else:
        await message.edit(des_, parse_mode="HTML")
