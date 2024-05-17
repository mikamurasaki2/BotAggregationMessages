# CREATE DATABASE maindb;
Use maindb;
drop table table_messages;
drop table table_replies;
drop table table_users_private;
drop table table_users;

create table table_messages
(
    id              int auto_increment
        primary key,
    message_id      bigint null,
    chat_id         bigint null,
    user_id         bigint null,
    message_text    text   null,
    chat_username   text   null,
    username        text   null,
    date            int    null,
    question_type   text   null,
    is_admin_answer tinyint(1) null
);

create table table_replies
(
    id                      int auto_increment
        primary key,
    message_text            text   null,
    username                text   null,
    date                    int    null,
    post_id                 bigint null,
    chat_id                 bigint null,
    user_id                 bigint null,
);

create table table_users
(
    id              int auto_increment
        primary key,
    chat_id         bigint     null,
    user_id         bigint     null,
    user_first_name text       null,
    user_last_name  text       null,
    username        text       null,
);

create table table_users_private
(
    id              int auto_increment
        primary key,
    user_id         bigint     null,
    password        text       null,
    username        text       null,
    date            bigint     null,
    user_first_name text       null,
    user_last_name  text       null,
    is_admin        tinyint(1) null
);