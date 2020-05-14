from bot import Life

import logging
from logging import handlers

logger = logging.getLogger('diorite')
logger.setLevel(logging.DEBUG)

handler = logging.handlers.RotatingFileHandler(filename='logs/granitepy.log', mode='w', backupCount=10)
handler.doRollover()

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s', datefmt=f'%d/%m/%Y %I:%M:%S %p')
handler.setFormatter(formatter)

logger.addHandler(handler)


if __name__ == '__main__':
    bot = Life()
    bot.run(bot.config.TOKEN)
