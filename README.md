# Life

Life is a multi-purpose discord bot made by Axel#3456. You can click 
[here](https://discord.com/oauth2/authorize?client_id=628284183579721747&scope=bot&permissions=4399156288) to invite it with basic permissions,
or [here](https://discord.com/oauth2/authorize?client_id=628284183579721747&scope=bot) to invite with no permissions. Feel free to join my 
[support server](https://discord.gg/w9f6NkQbde) in case you find any bugs or have features to suggest.


## Features:
* Music - lyrics, queue management, volume control, and filters
* Birthdays - Set your birthday and notify users of when a birthday happens so that you never forget.
* Economy system - XP, leaderboards, rank cards, and money.
* Image commands - Edit images from urls, attachments, or profile pictures. Supports different image formats such as gif, heic and svg.
* Information commands - Easily get yours or someone else's avatar, server icons/banners and other information.
* Tags - Create a tag, then easily fetch its content to store useful information or funny moments.
* Time - View another persons timezone and set reminders that can repeat on a fixed schedule.
* Todo - Set todos to keep track of things that need to be done.

## Links
* [Invite (Required permissions)](https://discord.com/oauth2/authorize?client_id=628284183579721747&scope=bot&permissions=4399156288)
* [Invite (No permissions)](https://discord.com/oauth2/authorize?client_id=628284183579721747&scope=bot)
* [Support Server](https://discord.gg/w9f6NkQbde)

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
