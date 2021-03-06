import logging
import StopGame
import MetaScore
import steam
import asyncio
import urllib.parse as urlp
import random
import os
import json
from translator import yandex_translate_question
from duckduckgo import ddg_search
import translator

from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = os.environ['API']
YANDEX_TOKEN = os.environ['YANDEX_TOKEN']

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
with open("steamlib.txt", "r") as file:
    steam_lib = json.load(file)
with open("top.txt", "r") as file:
    metacritic_top = json.load(file)
testing = False




@dp.message_handler(commands=['switch'])
async def translator(message: types.Message):
    if message.from_user.id != 196832767:
        await bot.send_message(message.chat.id, 'Nope, you are not allowed here')
        return
    trans = await yandex_translate_question("привет мир", YANDEX_TOKEN)
    await bot.send_message(message.chat.id, str(trans), parse_mode='HTML')
    global testing
    testing = not testing


@dp.message_handler(commands=['refresh'])
async def steam_app_lib_getter(message: types.Message):
    if message.from_user.id != 196832767:
        await bot.send_message(message.chat.id, 'Nope, you are not allowed here')
        return
    else:

        global steam_lib
        global metacritic_top
        try:
            steam_lib = await steam.get_steam_lib()
        except Exception:
            print("mc")
        try:
            metacritic_top = await MetaScore.metacritic_top()
        except Exception:
            print("mcmc")
        await bot.send_message(message.chat.id, "Refreshed, steam has {}, metatop has {}".format(len(steam_lib), len(metacritic_top)))
        await asyncio.sleep(3600 * 24)
        await steam_app_lib_getter(message)


def format_rating_answer(sg, mg):
    dictionary = {key: value for [key, value] in sg}
    result = list()
    for [key, value] in mg:
        result.append([key, str(value) + " <i> MScore</i>" + StopGame.formater_of_sg(dictionary, key)])
    formated = ["<b>{}</b> — {}".format(item[0], item[1]) for item in result]
    return '\n'.join(formated)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("""
    Hello!
    I'm would gladly help you to get some ideas about your's gaming
    
    <i>commands</i>:
     
    /s to search game, it's description and ratings.
    /r or /random to get random game with high ratings
    
    <i>example</i>: 
    /s Divinity
    /random
    """, parse_mode='HTML')


@dp.message_handler(commands=['s'])
async def title_search(message: types.Message):
    question = message.text[(len("/s")):]
    if question == "":
        await bot.send_message(message.chat.id,
                               "If you can't decide what are you going to look for, you should try my /r command!")
        return
    if testing:
        question = (await yandex_translate_question(question, YANDEX_TOKEN))
    ddc_link = await ddg_search(question)
    try:
        sgans = await StopGame.stop_game(question)
        mgans = await MetaScore.metacritic_search(question)
        image_web = mgans.pop()
        descr = mgans.pop()
        answer = format_rating_answer(sgans, mgans)
        image = None
        genres = []
        await bot.send_message(message.chat.id, "<b>" + str(mgans[0][0]) + "</b> " + descr, parse_mode='HTML')
        await bot.send_message(message.chat.id, 'These may also interest you!', parse_mode='HTML')
        await bot.send_message(message.chat.id, answer, parse_mode='HTML')
        if steam_lib.get(mgans[0][0]) is not None:
            image, genres = await steam.steam_get_game_info(str(steam_lib.get(mgans[0][0])))
            await bot.send_message(message.chat.id,
                                   'https://store.steampowered.com/app/{}'.format(
                                       urlp.quote_plus(str(steam_lib.get(mgans[0][0])))))
        else:
            await bot.send_message(message.chat.id, ddc_link, parse_mode="HTML")
        if image is not None:
            await bot.send_message(message.chat.id, "Genres: {}.".format(', '.join(genres)))
            await bot.send_message(message.chat.id, image, parse_mode='HTML')
        else:
            await bot.send_message(message.chat.id, image_web, parse_mode='HTML')
    except StopGame.StopError as err:
        await bot.send_message(message.chat.id, 'Somethind went wrong, got {} from stopgame'.format(err.code))
    except MetaScore.MetaError as err:
        await bot.send_message(message.chat.id, 'Somethind went wrong, got {} from metacritic'.format(err.code))
    except IndexError:
        await bot.send_message(message.chat.id, 'Nothing found', parse_mode='HTML')
    except Exception:
        await bot.send_message(message.chat.id, 'Nothing found, try again later', parse_mode='HTML')


@dp.message_handler(commands=['random', 'rand', 'r'])
async def rand_game(message: types.Message):
    choice = random.choice(metacritic_top)
    answer = "<i>Have you tried </i><b>{}</b><i>? Critics rate it </i><b>{}</b><i>/100," \
             " and gamers rate it </i><b>{}</b><i>/100, that's a lot!</i>" \
        .format(*choice)
    await bot.send_message(message.chat.id, answer, parse_mode='HTML')


@dp.message_handler()
async def echo(message: types.Message):
    await bot.send_message(message.chat.id, "<b>Me no speak amerikano, try using commands </b>, maybe you meant\n <b>/s {}</b>".format(message.text), parse_mode='HTML')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
