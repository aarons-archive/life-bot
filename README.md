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
2. Rename `config_example.py` to `config.py` [here](https://github.com/MyNameBeMrRandom/Life/tree/master/Life).

3. Fill in your discord bots token and PSQL connection info in the respective fields as seen below.
```python
DISCORD_TOKEN = "token"

DISCORD_PREFIX = "l-"

DB_CONN_INFO = {
    "user": "user-name",
    "password": "password",
    "host": "ip",
    "database": "database_name"
}

NODES = {"node_name": {"ip": "node_ip",
                       "port": "node_port",
                       "rest_uri": "node_url",
                       "password": "node_password",
                       "identifier": "node_custom_identifier",
                      }
         }

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

