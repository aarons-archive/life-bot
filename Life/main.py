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
#

import asyncio
import contextlib
import logging
import logging.handlers
import os
import sys

import prettify_exceptions
import setproctitle

from bot import Life


@contextlib.contextmanager
def logger():

    logs = {'discord': None, 'bot': None, 'cogs': None, 'managers': None, 'utilities': None}

    for log_name in logs.keys():

        log = logging.getLogger(log_name)
        handler = logging.handlers.RotatingFileHandler(filename=f'logs/{log_name}.log', mode='w', backupCount=5, encoding='utf-8', maxBytes=2**22)
        handler.setFormatter(logging.Formatter(f'%(asctime)s | %(levelname)s: %(name)s: %(message)s', datefmt='%d/%m/%Y at %I:%M:%S %p'))
        if os.path.isfile(f'logs/{log_name}.log'):
            handler.doRollover()
        log.addHandler(handler)

        logs[log_name] = log

    logs['discord'].setLevel(logging.INFO)
    logs['bot'].setLevel(logging.DEBUG)
    logs['cogs'].setLevel(logging.DEBUG)
    logs['managers'].setLevel(logging.DEBUG)
    logs['utilities'].setLevel(logging.DEBUG)

    try:
        yield
    finally:
        [log.handlers[0].close() for log in logs.values()]


if __name__ == '__main__':

    os.environ['JISHAKU_NO_UNDERSCORE'] = 'True'
    os.environ['JISHAKU_HIDE'] = 'True'
    os.environ['PY_PRETTIFY_EXC'] = 'True'

    setproctitle.setproctitle('Life')
    prettify_exceptions.hook()

    try:
        import uvloop
        if sys.platform != 'win32':
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        uvloop = None
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    else:
        del uvloop

    with logger():
        bot = Life()
        bot.run(bot.config.token)
