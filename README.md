# Life
[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/badges/60-percent-of-the-time-works-every-time.svg)](https://forthebadge.com)

Life is a multi-purpose discord bot made by Axel#3456. You can click 
[here](https://discord.com/oauth2/authorize?client_id=628284183579721747&scope=bot&permissions=4399156288) to invite it with basic permissions,
or [here](https://discord.com/oauth2/authorize?client_id=628284183579721747&scope=bot) to invite with no permissions. Feel free to join my 
[support server](https://discord.gg/w9f6NkQbde) in case you find any bugs or have features to suggest.

## Features:
* **Music** - lyrics, queue management, volume control, and filters
* **Birthdays** - Set your birthday and notify users of when a birthday happens so that you never forget.
* **Economy system** - XP, leaderboards, rank cards, and money.
* **Image commands** - Edit images from urls, attachments, or profile pictures. Supports different image formats such as gif, heic and svg.
* **Information commands** - Easily get yours or someone else's avatar, server icons/banners and other information.
* **Tags** - Create a tag, then easily fetch its content to store useful information or funny moments.
* **Time** - View another persons timezone and set reminders that can repeat on a fixed schedule.
* **Todo** - Set todos to keep track of things that need to be done.

## Links
* [Invite (Required permissions)](https://discord.com/oauth2/authorize?client_id=628284183579721747&scope=bot&permissions=4399156288)
* [Invite (No permissions)](https://discord.com/oauth2/authorize?client_id=628284183579721747&scope=bot)
* [Support Server](https://discord.gg/w9f6NkQbde)


# Running
I'd request that you don't run your own instance of this bot, but im not exactly able to stop you...setup instructions are provided 
for those wishing to contribute to the development of life.

### Prerequisites
* [Python-3.9](https://www.python.org/downloads) or higher
* [PostgreSQL-13](https://www.postgresql.org/download/) (a lower version should work, 13 is just the version I use.)
* [Redis](https://redis.io/topics/quickstart)
* [Obsidian](https://github.com/mixtape-bot/obsidian) (requires [JDK-16](https://openjdk.java.net/projects/jdk/16/))
* [Discord API Application](https://discord.com/developers/applications)
* [Spotify API Application](https://developer.spotify.com/dashboard/applications)
* [Ksoft.si API Application](https://api.ksoft.si/dashboard/)
* [AxelWeb](https://cdn.axelancerr.xyz/home) token (Reach out to me on discord if you desperately need this.)


* Good python knowledge, chances are that I'll help you understand whatever is going on here - as long as you know 
  [the basics](https://media.mrrandom.xyz/TofuYoyoCynicChorusGyro.png) of a discord bot made in python.
  
### Setup

1. Clone repository
```bash
git clone https://github.com/Axelancerr/Life
cd Life/
```

2. Create and activate a virtual environment

If needed, run `sudo apt install python3.9-venv`.
```bash
python -m venv venv/
source venv\bin\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Rename [`config_example.py`](config_example.py) to `config.py` and fill in the tokens/other data.
```bash
cd Life/
mv config_example.py Life/config.py
nano config.py
```

5. Run the [`main.py`](Life/main.py) file.
```bash
python main.py
```
