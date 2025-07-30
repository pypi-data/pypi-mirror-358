from asyncio import run
from PGram import Bot
from loader import TOKEN
from example.router import r

""" Basic example """
bot = Bot(TOKEN, routers=[r])
run(bot.start())
