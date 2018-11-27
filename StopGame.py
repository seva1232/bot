import requests
from bs4 import BeautifulSoup
import pprint
import re
from urllib.parse import quote_plus
import asyncio
import aiohttp


def formater_of_sg(dictionary, key):
    if key in dictionary.keys():
        return ", " + str(dictionary.get(key)) + ' <i>SGame</i>'
    else:
        return ''


def stop_game_request_parse(req):
    scores = list(re.findall(r'(?<=<span class="tag">)...(?=</span></div></div>)', req))
    titles = list(re.findall(r'(?<=" alt=")[-:\w, ]+(?="></a><div)', req))
    rating = list(map(list, (zip(titles, list(map(float, scores))))))
    for item in rating:
        item[1] *= 10
        item[1] = int(item[1])
    return rating


async def stop_game(question):
    url = "https://stopgame.ru/search/?s={}&where=games&sort=relevance".format(quote_plus(question))
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            site_text = await resp.text()
            answer = stop_game_request_parse(site_text)
            return answer


if __name__ == "__main__":
    title = input()
    url = "https://stopgame.ru/search/?s={}&where=games&sort=relevance".format(quote_plus(title))
    req = requests.get(url)
    print(req)
    ratings = stop_game_request_parse(req)
    pprint.pprint(ratings)
