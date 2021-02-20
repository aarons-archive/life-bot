# Life
Life is a discord bot coded by Axel#3456. Click the link below to invite it to your server and do `l-help` for more information.

Features:
* Rich command error feedback.
* Image manipulation/filter commands.
* Wide range of informational commands.
* Fully functional music system with spotify support through youtube. Playlists coming soon:tm:
* Reminders including support for natural language datetimes. (eg, `do this tomorrow`, `in 2h remember to do this`, `1st january 2021 birthday time!`)
* Guild and user config management.
* Birthday tracking.
* Time and timezone tracking.
* Basic economy functions.
* Todos.
* Tags.

## Links
* [Bot invite](https://discord.com/oauth2/authorize?client_id=628284183579721747&scope=bot&permissions=37080128)
* [Support Server](https://discord.gg/xP8xsHr)

## Installing/Running
While I would prefer you don't run your own instance of this bot, setup instructions will be provided for those wanting to contribute to the development of Life.

### Prerequisites
* Python3.8 or higher
* PostgreSQL-12
* Redis server
* A LavaLink node
* Spotify API credentials
* Ksoft.si API credentials
* Image uploader token

### Setup

1. Install dependencies
```bash
pip install -U -r requirements.txt
```

2. Rename `config_example.py` to `config.py` [here](https://github.com/Axelancerr/Life/tree/master/Life/config).
```bash
mv config_example.py config.py
```

3. Fill in the config file with the correct information.

4. Run the `main.py` file.
```bash
python3.8 main.py
```