import contextlib
import logging
import os
from logging.handlers import RotatingFileHandler

from bot import Life


@contextlib.contextmanager
def logger():

    log = logging.getLogger('diorite')
    log.setLevel(logging.DEBUG)

    handler = logging.handlers.RotatingFileHandler(filename='logs/diorite.log', mode='w',
                                                   backupCount=10, maxBytes=2**20)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                                           datefmt=f'%d/%m/%Y %I:%M:%S %p'))

    if os.path.isfile('logs/diorite.log'):
        handler.doRollover()

    log.addHandler(handler)

    try:
        yield
    finally:
        handler.close()


if __name__ == '__main__':
    with logger():
        bot = Life()
        bot.run(bot.config.TOKEN)
