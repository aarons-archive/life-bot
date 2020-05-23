# Life
Life is an RPG discord bot coded by MrRandom#9258. Click the link below to invite it to your discord server and do `l-help` for more information.

## Links
* [Bot invite](https://discordapp.com/oauth2/authorize?client_id=628284183579721747&scope=bot&permissions=103926848)
* [Support Server](https://discord.gg/xP8xsHr)
l
## Installing/Running
While I would prefer you don't run your own instance of this bot, setup instructions will be provided for those wanting to contribute to the development of Life.

### Prerequisites
* Python3.7 or higher
* PostgreSQL database
* A running lavalink node

### Setup
1. Install dependencies
```
pip install -U -r requirements.txt
```
2. Rename `config_example.py` to `config.py` [here](https://github.com/iDevision/Life/tree/master/Life).

3. Fill in the config file with the correct information as seen below.
```python
TOKEN = "BOT_TOKEN"
PREFIX = "BOT_PREFIX"

SPOTIFY_ID = "SPOTIFY APP ID"
SPOTIFY_SECRET = "SPOTIFY API SECRET"

DATABASE = {
    "host": "DATABASE IP",
    "user": "DATABASE USER",
    "password": "DATABASE PASSWORD",
    "database": "DATABASE NAME"
}

NODES = {
    "NODE 1": {
        "host": "LAVALINK NODE IP",
        "port": 00000, # LAVALINK NODE PORT
        "password": "LAVALINK NODE PASSWORD",
        "identifier": "LAVALINK NODE IDENTIFIER"
    }
}

EXTENSIONS = ['cogs.information', ...]
```

## Built with
* [asyncpg](https://github.com/MagicStack/asyncpg)
* [discord.py](https://github.com/Rapptz/discord.py)
* [jishaku](https://github.com/Gorialis/jishaku)
* [psutil](https://github.com/giampaolo/psutil)
* [matplotlib](https://github.com/matplotlib/matplotlib)
* [wand](https://github.com/emcconville/wand)
* [tabulate](https://github.com/astanin/python-tabulate)
* [spotify](https://github.com/mental32/spotify.py)
* [diorite](https://github.com/iDevision/diorite)
* [setproctitle](https://github.com/dvarrazzo/py-setproctitle)
* [lavalink](https://github.com/Frederikam/Lavalink)

