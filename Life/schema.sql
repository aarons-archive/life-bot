CREATE TABLE IF NOT EXISTS bot_usage(
    id BIGINT UNIQUE,
    usage json
);

CREATE TABLE IF NOT EXISTS bot_growth(
    date TEXT UNIQUE,
    member_count BIGINT,
    guild_count BIGINT
);




