create table table_messages
(
    id            INTEGER
        primary key auto_increment,
    message_id    BIGINT,
    chat_id       BIGINT,
    user_id       BIGINT,
    message_text  TEXT,
    chat_username TEXT,
    username      TEXT,
    date          DATETIME
);

create table table_replies
(
    id                      INTEGER
        primary key auto_increment,
    message_id              BIGINT,
    chat_id                 BIGINT,
    user_id                 BIGINT,
    message_text            TEXT,
    chat_username           TEXT,
    username                TEXT,
    date                    DATETIME,
    replied_to_user_id      BIGINT,
    replied_to_message_text TEXT,
    replied_to_message_id   BIGINT,
    replied_to_message_date TEXT
);

create table table_users
(
    id              INTEGER
        primary key auto_increment,
    chat_id         BIGINT,
    chat_username   TEXT,
    user_id         BIGINT,
    username        TEXT,
    user_first_name TEXT,
    user_last_name  TEXT
);

create table table_users_private
(
    id              INTEGER
        primary key auto_increment,
    user_id         BIGINT,
    password        TEXT,
    username        TEXT,
    user_first_name TEXT,
    user_last_name  TEXT,
    date            DATETIME
);