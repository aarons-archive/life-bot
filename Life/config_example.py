

# Bot
TOKEN = ''
PREFIX = 'l-'
EXTENSIONS = [
    'jishaku',
    'cogs.dev',
    'cogs.todo',
    'cogs.tags',
    'cogs.time',
    'cogs.kross',
    'cogs.images',
    'cogs.events',
    'cogs.economy',
    'cogs.settings',
    'cogs.birthdays',
    'cogs.information',
    'cogs.voice.music',
    'cogs.systemcollapse',
]
OWNER_IDS = {
    238356301439041536, 440113725970710528, 718259605523660870
}


# Tokens
AXEL_WEB_TOKEN = ''
KSOFT_TOKEN = ''
SPOTIFY_CLIENT_ID = ''
SPOTIFY_CLIENT_SECRET = ''


# Connection information
POSTGRESQL = {
    'host':     '',
    'user':     '',
    'database': '',
    'password': '',
}
REDIS = {
    'host':     '',
    'port':     0000,
    'password': '',
    'db':       0,
}
NODES = [
    {
        'host':       '',
        'port':       '',
        'identifier': '',
        'password':   '',
        'type':       '',
    },
    {
        'host':       '',
        'port':       '',
        'identifier': '',
        'password':   '',
        'type':       '',
    },
]


# Webhook URL's
ERROR_WEBHOOK_URL = ''
LOGGING_WEBHOOK_URL = ''
DM_WEBHOOK_URL = ''


# Custom values
COLOUR = 0xF1C40F
ZWSP = '\u200b'
NL = '\n'


# Emoji mappings
CHANNEL_EMOJIS = {
    'text':         '<:text:739399497200697465>',
    'text_locked':  '<:text_locked:739399496953364511>',
    'text_nsfw':    '<:text_nsfw:739399497251160115>',
    'news':         '<:news:739399496936718337>',
    'news_locked':  '<:news_locked:739399497062416435>',
    'voice':        '<:voice:739399497221931058>',
    'voice_locked': '<:voice_locked:739399496924135476>',
    'category':     '<:category:738960756233601097>'
}
BADGE_EMOJIS = {
    'staff':                  '<:staff:738961032109752441>',
    'partner':                '<:partner:738961058613559398>',
    'hypesquad':              '<:hypesquad:738960840375664691>',
    'bug_hunter':             '<:bug_hunter:738961014275571723>',
    'bug_hunter_level_2':     '<:bug_hunter_level_2:739390267949580290>',
    'hypesquad_bravery':      '<:hypesquad_bravery:738960831596855448>',
    'hypesquad_brilliance':   '<:hypesquad_brilliance:738960824327995483>',
    'hypesquad_balance':      '<:hypesquad_balance:738960813460684871>',
    'early_supporter':        '<:early_supporter:738961113219203102>',
    'system':                 '<:system_1:738960703284576378><:system_2:738960703288770650>',
    'verified_bot':           '<:verified_bot_1:738960728022581258><:verified_bot_2:738960728102273084>',
    'verified_bot_developer': '<:verified_bot_developer:738961212250914897>',
}
COMMON_EMOJIS = {
    'loading': '<a:loading:817924889271992320>'
}


# Dateparser settings
DATEPARSER_SETTINGS = {
    'DATE_ORDER':               'DMY',
    'TIMEZONE':                 'UTC',
    'RETURN_AS_TIMEZONE_AWARE': False,
    'PREFER_DAY_OF_MONTH':      'current',
    'PREFER_DATES_FROM':        'future',
    'PARSERS':                  ['relative-time', 'absolute-time', 'timestamp', 'custom-formats']
}
