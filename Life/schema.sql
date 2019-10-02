CREATE TABLE IF NOT EXISTS accounts(
    id BIGINT PRIMARY KEY,
    background TEXT,
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



