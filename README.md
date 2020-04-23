# Life
Life is an RPG discord bot coded by MrRandom#9258. Click the link below to invite it to your discord server and do `l-help` for more information.

## Links
* [Bot invite](https://discordapp.com/oauth2/authorize?client_id=628284183579721747&scope=bot)
* [Support Server](https://discord.gg/xP8xsHr)

## Installing/Running
While I would prefer you don't run your own instance of this bot, setup instructions will be provided for those wanting to contribute to the development of Life.

### Prerequisites
* Python3.6 or higher
* PostgreSQL database
* A running andesite node

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

OSU_TOKEN = "OSU API KEY"

SPOTIFY_ID = "SPOTIFY APP ID"
SPOTIFY_SECRET = "SPOTIFY API SECRET"

DATABASE = {
    "user": "DATABASE USER",
    "password": "DATABASE PASSWORD",
    "host": "DATABASE HOST IP",
    "database": "DATABASE NAME"
}

NODES = {
    "NODE 1": {
        "host": "ANDESITE NODE IP",
        "port": 00000, # ANDESITE NODE PORT
        "password": "ANDESITE NODE PASSWORD",
        "identifier": "CUSTOM ANDESITE NODE IDENTIFIER"
    }
}


EXTENSIONS = [
    "cogs.help",
    "cogs.events",
    "cogs.background",
    "jishaku",
    "cogs.dev",
    "cogs.information",
    "cogs.images",
    "cogs.todo",
    "cogs.voice.music",
    "cogs.voice.playlists",
    "cogs.kross",
]
```

## Built with
* [discord.py](https://github.com/Rapptz/discord.py)
* [asyncpg](https://github.com/MagicStack/asyncpg)
* [psutil](https://github.com/giampaolo/psutil)
* [jishaku](https://github.com/Gorialis/jishaku)
* [Pillow](https://github.com/python-pillow/Pillow)
* [matplotlib](https://github.com/matplotlib/matplotlib)
* [andesite](https://github.com/natanbc/andesite-node)
* [granitepy](https://github.com/iDevision/granitepy)
* [aiOsu](https://github.com/iDevision/aiOsu)

