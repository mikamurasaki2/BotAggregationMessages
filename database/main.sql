create table table_messages
(
    id            int auto_increment
        primary key,
    message_id    bigint  null,
    chat_id       bigint  null,
    user_id       bigint  null,
    message_text  text null,
    chat_username text null,
    username      text null,
    date          int  null
);

create table table_replies
(
    id                      int auto_increment
        primary key,
    message_id              bigint  null,
    chat_id                 bigint  null,
    user_id                 bigint  null,
    message_text            text null,
    chat_username           text null,
    username                text null,
    date                    int  null,
    replied_to_user_id      bigint  null,
    replied_to_message_text text null,
    replied_to_message_id   bigint  null,
    replied_to_message_date text null,
    post_id                 bigint  null
);

create table table_users
(
    id              int auto_increment
        primary key,
    chat_id         bigint  null,
    chat_username   text null,
    user_id         bigint  null,
    username        text null,
    user_first_name text null,
    user_last_name  text null
);

create table table_users_private
(
    id              int auto_increment
        primary key,
    user_id         bigint  null,
    password        text null,
    username        text null,
    user_first_name text null,
    user_last_name  text null,
    date            int  null
);