CREATE TABLE IF NOT EXISTS users(
    id BIGINT PRIMARY KEY,
    background TEXT,
    voted BOOLEAN,
    vote_claimed BOOLEAN,
    vote_count BIGINT,
    cash BIGINT,
    bank BIGINT
);

CREATE TABLE IF NOT EXISTS user_blacklist(
    id BIGINT PRIMARY KEY,
    reason TEXT
);

CREATE TABLE IF NOT EXISTS guild_blacklist(
    id BIGINT PRIMARY KEY,
    reason TEXT
);



