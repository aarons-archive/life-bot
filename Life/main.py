import contextlib
import logging
import os
from logging.handlers import RotatingFileHandler

from bot import Life


@contextlib.contextmanager
def logger():

    log_format = '%(asctime)s - %(name)s - %(levelname)s: %(message)s'
    date_format = f'%d/%m/%Y %H:%M:%S'

    diorite_log = logging.getLogger('diorite')
    diorite_log.setLevel(logging.DEBUG)
    diorite_handler = RotatingFileHandler(filename='logs/diorite.log', mode='w', backupCount=5, encoding='utf-8',
                                          maxBytes=2**20)
    diorite_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    if os.path.isfile('logs/diorite.log'):
        diorite_handler.doRollover()
    diorite_log.addHandler(diorite_handler)

    bot_log = logging.getLogger('Life')
    bot_log.setLevel(logging.DEBUG)
    bot_handler = RotatingFileHandler(filename='logs/bot.log', mode='w', backupCount=5, encoding='utf-8',
                                      maxBytes=2**20)
    bot_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    if os.path.isfile('logs/bot.log'):
        bot_handler.doRollover()
    bot_log.addHandler(bot_handler)

    discord_log = logging.getLogger('discord')
    discord_log.setLevel(logging.INFO)
    discord_handler = RotatingFileHandler(filename='logs/discord.log', mode='w', backupCount=5, encoding='utf-8',
                                          maxBytes=2**20)
    discord_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    if os.path.isfile('logs/discord.log'):
        discord_handler.doRollover()
    discord_log.addHandler(discord_handler)

    try:
        yield
    finally:
        diorite_handler.close()
        bot_handler.close()
        discord_handler.close()


if __name__ == '__main__':
    with logger():
        bot = Life()
        bot.run(bot.config.TOKEN)
