import aiohttp
from urllib.parse import urlparse


async def yandex_translate_question(question: str, TOKEN: str):
    TRANSLATOR_API = "https://translate.yandex.net/api/v1.5/tr.json/translate"
    params = {
        'key': TOKEN,
        "lang": 'eng',
        'text': question,
        'format': 'plain'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(TRANSLATOR_API, params=params) as resp:
            text = await resp.json()
            return text
