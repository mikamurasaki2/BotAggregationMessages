from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pymysql
# import mysql.connector
from config import *
import database.models as models
#import models


engine = create_engine('mysql+mysqlconnector://root:@localhost/maindb')
Session = sessionmaker(bind=engine)


def get_db():
    try:
        return Session()
    except Exception as e:
        raise Exception(e)


# INSERTS
def insert_private_user(data):
    with get_db() as db:
        new_user = models.PrivateUser(user_id=data['user_id'], password=data['password'], username=data['username'],
                                      user_first_name=data['user_first_name'], user_last_name=data['user_last_name'],
                                      date=data['date'])
        db.add(new_user)
        db.commit()


def insert_user(data):
    with get_db() as db:
        new_user = models.User(chat_id=data['chat_id'], chat_username=data['chat_username'], user_id=data['user_id'],
                               username=data['username'], user_first_name=data['user_first_name'],
                               user_last_name=data['user_last_name'])
        db.add(new_user)
        db.commit()


def insert_message(data):
    with get_db() as db:
        new_message = models.Message(message_id=data['message_id'], chat_id=data['chat_id'], user_id=data['user_id'],
                                     message_text=data['message_text'], chat_username=data['chat_username'],
                                     username=data['username'], date=data['date'])
        db.add(new_message)
        db.commit()


def insert_reply(data):
    with get_db() as db:
        new_reply = models.Reply(message_id=data['message_id'], chat_id=data['chat_id'], user_id=data['user_id'],
                                 message_text=data['message_text'], chat_username=data['chat_username'],
                                 username=data['username'], date=data['date'],
                                 replied_to_user_id=data['replied_to_user_id'],
                                 replied_to_message_text=data['replied_to_message_text'],
                                 replied_to_message_id=data['replied_to_message_id'],
                                 replied_to_message_date=data['replied_to_message_date'])
        db.add(new_reply)
        db.commit()


# CHECKS
def check_private_user(user_id):
    with get_db() as db:
        user = db.query(models.PrivateUser).filter(models.PrivateUser.user_id == user_id).first()
        if user:
            return True
        else:
            return False


def check_user(user_id, chat_id):
    with get_db() as db:
        is_user_id = db.query(models.User).filter(models.User.user_id == user_id).first()
        is_chat_id = db.query(models.User).filter(models.User.chat_id == chat_id).first()
        if is_user_id == is_chat_id:
            return True
        else:
            return False


def check_message(message_id):
    with get_db() as db:
        msg = db.query(models.Message).filter(models.Message.message_id == message_id).first()
        if msg:
            return True
        else:
            return False
