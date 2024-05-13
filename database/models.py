from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Message(Base):
    __tablename__ = 'table_messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer)
    chat_id = Column(Integer)
    user_id = Column(Integer)
    message_text = Column(Text)
    chat_username = Column(String)
    username = Column(String)
    date = Column(Integer)
    question_type = Column(Text)
    is_admin_answer = Column(Integer)


class Reply(Base):
    __tablename__ = 'table_replies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer)
    chat_id = Column(Integer)
    user_id = Column(Integer)
    message_text = Column(Text)
    chat_username = Column(String)
    username = Column(String)
    date = Column(Integer)
    replied_to_user_id = Column(Integer)
    replied_to_message_text = Column(Text)
    replied_to_message_id = Column(Integer)
    replied_to_message_date = Column(Text)
    post_id = Column(Integer)


class User(Base):
    __tablename__ = 'table_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer)
    chat_username = Column(String)
    user_id = Column(Integer)
    username = Column(String)
    user_first_name = Column(String)
    user_last_name = Column(String)
    is_admin = Column(Boolean)


class PrivateUser(Base):
    __tablename__ = 'table_users_private'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    password = Column(Text)
    username = Column(String)
    user_first_name = Column(String)
    user_last_name = Column(String)
    date = Column(Integer)
    is_admin = Column(Boolean)
