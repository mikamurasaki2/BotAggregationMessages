from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pymysql
# import mysql.connector
from config import *
import database.models as models

# import models

#engine = create_engine('mysql+mysqlconnector://root:@localhost/md1')
engine = create_engine('mysql+mysqlconnector://root:root@localhost/maindb')
Session = sessionmaker(bind=engine)


def get_db():
    try:
        return Session()
    except Exception as e:
        raise Exception(e)


# INSERTS

# Добавление пользователя в users_private
def insert_private_user(data):
    with get_db() as db:
        new_user = models.PrivateUser(user_id=data['user_id'], password=data['password'], username=data['username'],
                                      user_first_name=data['user_first_name'], user_last_name=data['user_last_name'],
                                      date=data['date'], is_admin=data['is_admin'])
        db.add(new_user)
        db.commit()


# Добавление участника группового чата
def insert_user(data):
    with get_db() as db:
        new_user = models.User(chat_id=data['chat_id'], chat_username=data['chat_username'], user_id=data['user_id'],
                               username=data['username'], user_first_name=data['user_first_name'],
                               user_last_name=data['user_last_name'], is_admin=data['is_admin'])
        db.add(new_user)
        db.commit()


# Добавление сообщения в бд
def insert_message(data):
    with get_db() as db:
        new_message = models.Message(message_id=data['message_id'], chat_id=data['chat_id'], user_id=data['user_id'],
                                     message_text=data['message_text'], chat_username=data['chat_username'],
                                     username=data['username'], date=data['date'], question_type=data['question_type'],
                                     is_admin_answer=data['is_admin_answer'])
        db.add(new_message)
        db.commit()


# Добавление ответного сообщения на вопрос в бд
def insert_reply(data):
    with get_db() as db:
        new_reply = models.Reply(message_id=data['message_id'], chat_id=data['chat_id'], user_id=data['user_id'],
                                 message_text=data['message_text'], chat_username=data['chat_username'],
                                 username=data['username'], date=data['date'],
                                 replied_to_user_id=data['replied_to_user_id'],
                                 replied_to_message_text=data['replied_to_message_text'],
                                 replied_to_message_id=data['replied_to_message_id'],
                                 replied_to_message_date=data['replied_to_message_date'],
                                 post_id=data['replied_to_message_id'])
        db.add(new_reply)
        db.commit()


# Добавление анонима в таблице зарегистрированных пользователей
def insert_anon_private_user(data):
    with get_db() as db:
        new_user = models.PrivateUser(user_id=data['user_id'], password=data['password'], username=data['username'],
                                      user_first_name=data['user_first_name'], user_last_name=data['user_last_name'],
                                      date=data['date'], is_admin=data['is_admin'])
        db.add(new_user)
        db.commit()


# CHECKS

# Проверка на уникальность добавляемого пользователя при регистрации
def check_private_user(user_id):
    with get_db() as db:
        user = db.query(models.PrivateUser).filter(models.PrivateUser.user_id == user_id).first()
        if user:
            return True
        else:
            return False


# Проверка на то, что пользователь уже является участником чата
def check_user(user_id, chat_id):
    with get_db() as db:
        users = db.query(models.User).filter(models.User.user_id == user_id).all()
        if users:
            chats = [user.chat_id for user in users]
            if chat_id not in chats:
                return True
            else:
                return False
        else:
            return True


# Проверка отправляемого вопроса
def check_message(message_id):
    with get_db() as db:
        msg = db.query(models.Message).filter(models.Message.message_id == message_id).first()
        if msg:
            return True
        else:
            return False


# Проверка, что ответное сообщение на вопрос было от админа
def check_reply_is_admin(user_id):
    with get_db() as db:
        user = user = db.query(models.PrivateUser).filter(models.PrivateUser.user_id == user_id).first()
        if user and user.is_admin:
            return 1
        else:
            return 0


# GETS

# Получение имени пользователя
def get_first_name(user_id):
    with get_db() as db:
        user = db.query(models.PrivateUser).filter(models.PrivateUser.user_id == user_id).first()
        if user:
            return user.user_first_name
        else:
            return None


# Получение фамилии пользователя
def get_last_name(user_id):
    with get_db() as db:
        user = db.query(models.PrivateUser).filter(models.PrivateUser.user_id == user_id).first()
        if user:
            return user.user_last_name
        else:
            return None


# Получения уникального индентификатора пользователя
def get_user_id(user_id):
    with get_db() as db:
        user = db.query(models.PrivateUser).filter(models.PrivateUser.user_id == user_id).first()
        if user:
            return user.user_id
        else:
            return None


# DELETE

# Удаление пользователя
def delete_user(user_id):
    with get_db() as db:
        user = db.query(models.PrivateUser).filter(models.PrivateUser.user_id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        else:
            return False


# Изменение статуса вопроса на "Админ дал ответ", если админ дал ответ
def edit_message_have_admin_answer(message_id, chat_id):
    with get_db() as db:
        message = db.query(models.Message).filter(models.Message.message_id == message_id, models.Message.chat_id == chat_id).first()
        if message:
            message.is_admin_answer = 1
            db.commit()
            return True
        else:
            return False
