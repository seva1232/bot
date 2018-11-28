import logging
import StopGame
import MetaScore
import API
import steam
import asyncio
import urllib.parse as urlp
import random
import os

from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = os.environ['API']

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
steam_lib = dict()
metacritic_top = list()


@dp.message_handler(commands=['refresh'])
async def steam_app_lib_getter(message: types.Message):
    if message.from_user.id != 196832767:
        await bot.send_message(message.chat.id, 'Nope, you are not allowed here')
        return
    else:
        global steam_lib
        global metacritic_top
        steam_lib = await steam.get_steam_lib()
        metacritic_top = await MetaScore.metacritic_top()
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
    try:
        sgans = await StopGame.stop_game(question)
        mgans = await MetaScore.metacritic_search(question)
        image_web = mgans.pop()
        descr = mgans.pop()
        answer = format_rating_answer(sgans, mgans)
        await bot.send_message(message.chat.id, "<b>" + str(mgans[0][0]) + "</b> " + descr, parse_mode='HTML')
        await bot.send_message(message.chat.id, image_web, parse_mode='HTML')
        await bot.send_message(message.chat.id, 'These may also interest you!', parse_mode='HTML')
        await bot.send_message(message.chat.id, answer, parse_mode='HTML')
        if steam_lib.get(mgans[0][0]) is not None:
            await bot.send_message(message.chat.id,
                                   'https://store.steampowered.com/app/{}'.format(
                                       urlp.quote_plus(str(steam_lib.get(mgans[0][0])))))
    except IndexError:
        await bot.send_message(message.chat.id, 'Nothing found', parse_mode='HTML')


@dp.message_handler(commands=['random', 'rand', 'r'])
async def rand_game(message: types.Message):
    choice = random.choice(metacritic_top)
    answer = "<i>Have you tried </i><b>{}</b><i>? Critics rate it </i><b>{}</b><i>/100," \
             " and gamers rate it </i><b>{}</b><i>/100, that's a lot!</i>"\
        .format(*choice)
    await bot.send_message(message.chat.id, answer, parse_mode='HTML')


@dp.message_handler()
async def echo(message: types.Message):
    await bot.send_message(message.chat.id, "<b>Me no speak amerikano, try using commands </b>", parse_mode='HTML')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
