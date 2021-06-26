#  Life
#  Copyright (C) 2020 Axel#3456
#
#  Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later version.
#
#  Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
#  PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with Life. If not, see https://www.gnu.org/licenses/.

import asyncio
import contextlib
import logging
import logging.handlers
import os
import sys
from typing import Any

import setproctitle

import config
from bot import Life


RESET = '\u001b[0m'
BOLD = '\u001b[1m'
UNDERLINE = '\u001b[4m'
REVERSE = '\u001b[7m'
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = [f'\u001b[{30 + i}m' for i in range(8)]


@contextlib.contextmanager
def logger():

    loggers: dict[str, logging.Logger] = {
        'discord':   logging.getLogger('discord'),
        'bot':       logging.getLogger('bot'),
        'cogs':      logging.getLogger('cogs'),
        'utilities': logging.getLogger('utilities'),
        'slate':     logging.getLogger('slate'),
    }

    for name, log in loggers.items():

        file_handler = logging.handlers.RotatingFileHandler(filename=f'logs/{name}.log', mode='w', backupCount=5, encoding='utf-8', maxBytes=2 ** 22)
        log.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        log.addHandler(stream_handler)

        if os.path.isfile(f'logs/{name}.log'):
            file_handler.doRollover()

        file_formatter = logging.Formatter(fmt='%(asctime)s [%(name) 30s] [%(filename) 20s] [%(levelname) 7s] %(message)s', datefmt='%I:%M:%S %p %d/%m/%Y')
        file_handler.setFormatter(file_formatter)

        stream_formatter = logging.Formatter(fmt=f'{CYAN}%(asctime)s{RESET} {YELLOW}[%(name) 30s]{RESET} {GREEN}[%(filename) 20s]{RESET} {BOLD}{REVERSE}{MAGENTA}[%(levelname) 7s]{RESET} %(message)s', datefmt='%I:%M:%S %p %d/%m/%Y')
        stream_handler.setFormatter(stream_formatter)

    loggers['discord'].setLevel(logging.INFO)
    loggers['bot'].setLevel(logging.DEBUG)
    loggers['cogs'].setLevel(logging.DEBUG)
    loggers['utilities'].setLevel(logging.DEBUG)
    loggers['slate'].setLevel(logging.INFO)

    try:
        yield
    finally:
        [log.handlers[0].close() for log in loggers.values()]


if __name__ == '__main__':

    os.environ['JISHAKU_NO_UNDERSCORE'] = 'True'
    os.environ['JISHAKU_HIDE'] = 'True'
    os.environ['JISHAKU_NO_DM_TRACEBACK'] = 'True'

    setproctitle.setproctitle('Life')

    try:
        import uvloop
        if sys.platform != 'win32':
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        uvloop = None
    else:
        del uvloop

    with logger():
        Life().run(config.TOKEN)
