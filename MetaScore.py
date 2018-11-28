import requests
import re
from urllib.parse import quote_plus
import asyncio
import aiohttp


def image_getter(req_text):
    image = (list(re.findall(r'(?<=<div class="result_thumbnail">\n)[ ]+<img src="[-\d\w:./]+', req_text)))[0]
    image = image.lstrip()
    image = image.split('"')[-1]
    # print(image)
    return image


def metacritic_parse(req_text):
    trashtitles = list(re.findall(r'class="product_title basic_stat"\S\n\s[ ]+[-/\w< ="]+>\n[ ]+[-\w: ]+(?=\n)', req_text))
    titles = list()
    for title in trashtitles:
        q = title.split("\n")
        q = q[-1].lstrip()
        q = re.sub(' IV', ' 4', q)
        q = re.sub(' III', ' 3', q)
        q = re.sub(' II', ' 2', q)
        titles.append(q)

    description = (list(re.findall(r'(?<=<p class="deck basic_stat">)[-\w :,.]+(?=</p>)', req_text)))[0]
    junkratings = list(re.findall(r'(?<=<span class="metascore_w medium game)[\w ]+">[\w \d]+(?=</span>)', req_text))
    ratings = list()
    for rating in junkratings:
        q = rating.split(">")
        q = q[-1].lstrip()
        ratings.append(q)
    ratingsv1 = list()
    for item in ratings:
        try:
            ratingsv1.append(int(item))
        except Exception:
            ratingsv1.append(item)
    res = list(map(list, zip(titles, ratingsv1)))
    # print("from parser", res)
    res.append(description)
    return res


# <div class="metascore_w small game positive">96</div>
# <span class="data textscore textscore_outstanding">9.1</span>

# async def metacritic_top():
def metacritic_top():
    site_texts = list()
    headers = {
        "authority": "www.metacritic.com",
        "user-agent": "Mozilla / 5.0(Windows NT 10.0;Win64;x64)"
    }
    url = "https://www.metacritic.com/browse/games/score/metascore/all/pc/filtered"
    for i in range(10):
            if i == 0:
                urll = url
            else:
                urll = url + '?page=' + str(i)
            site_texts.append(requests.get(urll, headers=headers).text)
        # async with aiohttp.ClientSession() as session:
        #     if i == 0:
        #         urll = url
        #     else:
        #         urll = url + '?page=' + str(i)
        #     async with session.get(urll, headers=headers) as resp:
        #         site_texts.append(await resp.text())
    titles = list()
    msrating = list()
    ursrating = list()
    for site in site_texts:
        msratingsite = list(re.findall(r'(?<=<div class="metascore_w small game positive">)..', site))
        userratingsite = list(re.findall(r'(?<=<span class="data textscore textscore_)[\w]+">...', site))
        trashtitles = list(
            re.findall(r'class="basic_stat product_title"\S\n\s[ ]+[-/\w< ="]+>\n[ ]+[-\w: ]+(?=\n)', site))
        titlessite = list()
        for title in trashtitles:
            q = title.split("\n")
            q = q[-1].lstrip()
            titlessite.append(q)
        titles.extend(titlessite)
        titlessite.clear()
        msrating.extend(msratingsite)
        msratingsite.clear()
        ursrating.extend(userratingsite)
        userratingsite.clear()
        trashtitles.clear()
    # ms_usr = [first + " " + second for first, second in zip[msrating, ursrating]] # hz
    ursrating = list(map(lambda x: x.split('>')[-1], ursrating))
    top_games = list(map(list, (titles, msrating, ursrating)))
    from pprint import pprint
    pprint(top_games)
    # return top_games


    # return {"Divinity" : 'top'}


async def metacritic_search(question):
    headers = {
        "authority": "www.metacritic.com",
        "user-agent": "Mozilla / 5.0(Windows NT 10.0;Win64;x64)"
    }
    url = "https://www.metacritic.com/search/game/{}/results?plats[3]=1&search_type=advanced".format(quote_plus(question))
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            site_text = await resp.text()
            answer = metacritic_parse(site_text)
            answer.append(image_getter(site_text))
            return answer

if __name__ ==  "__main__":
    metacritic_top()
    pass