CREATE TABLE IF NOT EXISTS bot_usage(
    id BIGINT UNIQUE,
    usage json
);

CREATE TABLE IF NOT EXISTS bot_growth(
    date TEXT UNIQUE,
    member_count BIGINT,
    guild_count BIGINT
);

CREATE TABLE IF NOT EXISTS user_blacklist(
    id BIGINT UNIQUE,
    reason TEXT
);

CREATE TABLE IF NOT EXISTS guild_blacklist(
    id BIGINT UNIQUE,
    reason TEXT
);