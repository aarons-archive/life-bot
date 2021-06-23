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

import setproctitle

import config
from bot import Life


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

        handler = logging.handlers.RotatingFileHandler(filename=f'logs/{name}.log', mode='w', backupCount=5, encoding='utf-8', maxBytes=2 ** 22)
        log.addHandler(handler)

        if os.path.isfile(f'logs/{name}.log'):
            handler.doRollover()

        handler.setFormatter(logging.Formatter(fmt='%(asctime)s | %(levelname)s: %(name)s: %(message)s', datefmt='%d/%m/%Y at %I:%M:%S %p'))

    loggers['discord'].setLevel(logging.INFO)
    loggers['bot'].setLevel(logging.DEBUG)
    loggers['cogs'].setLevel(logging.DEBUG)
    loggers['utilities'].setLevel(logging.DEBUG)
    loggers['slate'].setLevel(logging.DEBUG)

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
