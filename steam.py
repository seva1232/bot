import aiohttp
import json


async def get_steam_lib():
    url_steam_api = 'https://api.steampowered.com/ISteamApps/GetAppList/v2/'
    async with aiohttp.ClientSession() as session:
        async with session.get(url_steam_api) as resp:
            site_text = await resp.text()
    d = json.loads(site_text)
    ids_list = [item.get('appid') for item in d['applist']['apps']]
    names_list = [item.get('name') for item in d['applist']['apps']]
    steam_app_lib = dict(zip(names_list, ids_list))
    return steam_app_lib


async def steam_get_game_info(game_id):
    url = 'https://store.steampowered.com/api/appdetails/?appids=' + game_id
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            game_data = json.loads(await resp.text(), encoding='utf-8')
    image = game_data[game_id].get('data').get('header_image')
    genres = [item.get('description') for item in game_data[game_id].get('data').get('genres')]
    return image, genres
