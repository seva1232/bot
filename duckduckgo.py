import re
from urllib.parse import quote_plus, unquote_plus
import aiohttp


def ddg_parse(text_site):
    first_link = re.findall(r'(?<=class="result__a" href=").+(?=">)', text_site)[0]
    first_link = re.findall(r'http.+', first_link)[0]
    return first_link


async def ddg_search(question):
    url = 'https://duckduckgo.com/html?q={}'.format(quote_plus(question + " play game "))
    headers = {
        "user-agent": "Mozilla / 5.0(Windows NT 10.0;Win64;x64)"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            site_text = await resp.text()
            answer = ddg_parse(unquote_plus(site_text))
            return answer


if __name__ == "__main__":
    from requests import get
    question = input(":>")
    url = 'https://duckduckgo.com/html?q={}'.format(quote_plus(question + " play game "))
    req = get(url=url)
    with open("../text.html", "w") as file:
        file.write(req.text)
    print(ddg_parse(unquote_plus(req.text)))
    print(ddg_parse((req.text)))
