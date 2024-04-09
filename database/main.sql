create table table_messages
(
    id            INTEGER
        primary key auto_increment,
    message_id    INTEGER,
    chat_id       INTEGER,
    user_id       INTEGER,
    message_text  TEXT,
    chat_username TEXT,
    username      TEXT,
    date          INTEGER
);

create table table_replies
(
    id                      INTEGER
        primary key auto_increment,
    message_id              INTEGER,
    chat_id                 INTEGER,
    user_id                 INTEGER,
    message_text            TEXT,
    chat_username           TEXT,
    username                TEXT,
    date                    INTEGER,
    replied_to_user_id      INTEGER,
    replied_to_message_text TEXT,
    replied_to_message_id   INTEGER,
    replied_to_message_date TEXT
);

create table table_users
(
    id              INTEGER
        primary key auto_increment,
    chat_id         INTEGER,
    chat_username   TEXT,
    user_id         INTEGER,
    username        TEXT,
    user_first_name TEXT,
    user_last_name  TEXT
);

create table table_users_private
(
    id              INTEGER
        primary key auto_increment,
    user_id         INTEGER,
    password        TEXT,
    username        TEXT,
    user_first_name TEXT,
    user_last_name  TEXT,
    date            INTEGER
);