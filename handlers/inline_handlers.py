from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from database.database import Database
from filters.chat_filters import ChatTypeFilter
from keyboards import inline_buttons

router = Router()


class Ask_Question(StatesGroup):
    question = State()


# Создаем дб с таблицей
db_example = Database('example.db')

# таблица с данными пользователей лс
columns_users_private = [('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                         ('user_id', 'INTEGER'),
                         ('password', 'TEXT'),
                         ('username', 'TEXT'),
                         ('user_first_name', 'TEXT'),
                         ('user_last_name', 'TEXT'),
                         ('date', 'INTEGER')]
db_example.create_table('table_users_private', columns_users_private)


# Внесение данных юзеров в таблицу бд через ЛС
@router.message(ChatTypeFilter(chat_type=["private"]), Command('registration'))
async def cmd_reg(message: Message):
    # Добавляем пользователей в БД при нажатии /reg
    data_for_db = {
        'user_id': message.from_user.id,
        'password': None,
        'username': message.from_user.username,
        'user_first_name': message.from_user.first_name,
        'user_last_name': message.from_user.last_name,
        'date': message.date,
    }
    # Попытка проверить, что пользовтель не сущесвтует
    if db_example.check_value('table_users_private', 'user_id', message.from_user.id):
        db_example.insert_data('table_users_private', data_for_db)
    else:
        print("Пользователь уже существует!")
    await message.answer(f'Спасибо, вы внесены в базу данных!'
                         f'\nВаш логин для регистрации в веб-приложении: {message.from_user.id}')


# таблица с участниками чата
columns_users = [('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                 ('chat_id', 'INTEGER'),
                 ('chat_username', 'TEXT'),
                 ('user_id', 'INTEGER'),
                 ('username', 'TEXT'),
                 ('user_first_name', 'TEXT'),
                 ('user_last_name', 'TEXT')]
db_example.create_table('table_users', columns_users)


# Внесение данных юзеров в таблицу бд
@router.message(ChatTypeFilter(chat_type=["group"]), Command('start'))
async def cmd_start(message: Message):
    # Добавляем пользователей в БД при нажатии /start
    data_for_db = {
        'chat_id': message.chat.id,
        'chat_username': message.chat.username,
        'user_id': message.from_user.id,
        'username': message.from_user.username,
        'user_first_name': message.from_user.first_name,
        'user_last_name': message.from_user.last_name
    }
    # Попытка проверить, что пользовтель не сущесвтует
    if db_example.check_value('table_users', 'user_id', message.from_user.id) or db_example.check_value('table_users',
                                                                                                        'chat_id',
                                                                                                        message.chat.id):
        db_example.insert_data('table_users', data_for_db)
    else:
        print("Пользователь уже существует")


# Тест сообщения с инлайн кнопками
@router.message(ChatTypeFilter(chat_type=["group"]), Command('service'))
async def cmd_main(message: Message):
    await message.answer('Это основное сообщение тестирования команды /main',
                         reply_markup=inline_buttons.main_kb)


# таблица с данными сообщений
columns_messages = [('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                    ('message_id', 'INTEGER'),
                    ('chat_id', 'INTEGER'),
                    ('user_id', 'INTEGER'),
                    ('message_text', 'TEXT'),
                    ('chat_username', 'TEXT'),
                    ('username', 'TEXT'),
                    ('date', 'INTEGER')
                    ]
db_example.create_table('table_messages', columns_messages)


# @router.message(F.photo)
# async def get_photo(message: Message):
#     await message.bot.download(file=message.photo[-1].file_id, destination=file_name)

# Ловим состояние ввода вопроса пользователя
@router.message(ChatTypeFilter(chat_type=["group"]), Ask_Question.question)
async def second_step_asking_question(message: Message, state: FSMContext):
    await state.update_data(question=message.text)
    data = await state.get_data()  # ХРАНИТСЯ АЙДИ СООБЩЕНИЯ И ТЕКСТ СООБЩЕНИЯ
    print(data)
    data_for_db = {'message_id': message.message_id,
                   'chat_id': message.chat.id,
                   'user_id': message.from_user.id,
                   'message_text': message.text,
                   'chat_username': message.chat.username,
                   'username': message.from_user.username,
                   'date': message.date,
                   }
    db_example.insert_data('table_messages', data_for_db)
    await message.answer(f'Спасибо, ваш вопрос принят!'
                         f'\nВопрос задан: {message.from_user.id}'
                         f'\nВаш вопрос: {data["question"]}',
                         reply_markup=inline_buttons.delete_kb)
    await state.clear()  # чтобы не засорялся, у пользователя слетало состояние


# таблица с данными сообщений
columns_replies = [('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                   ('message_id', 'INTEGER'),
                   ('chat_id', 'INTEGER'),
                   ('user_id', 'INTEGER'),
                   ('message_text', 'TEXT'),
                   ('chat_username', 'TEXT'),
                   ('username', 'TEXT'),
                   ('date', 'INTEGER'),
                   ('replied_to_user_id', 'INTEGER'),
                   ('replied_to_message_text', 'TEXT'),
                   ('replied_to_message_id', 'INTEGER'),
                   ('replied_to_message_date', 'TEXT')
                   ]
db_example.create_table('table_replies', columns_replies)


# Сохраняем только реплаи, которые были даны на вопросы через бот
@router.message(ChatTypeFilter(chat_type=["group"]))
async def process_message(message: Message):
    # Check if the message is a reply
    if message.reply_to_message:
        if not db_example.check_value('table_messages', 'message_id', message.reply_to_message.message_id):
            data_for_db = {'message_id': message.message_id,
                           'chat_id': message.chat.id,
                           'user_id': message.from_user.id,
                           'message_text': message.text,
                           'chat_username': message.chat.username,
                           'username': message.from_user.username,
                           'date': message.date,
                           'replied_to_user_id': message.reply_to_message.from_user.id if message.reply_to_message else None,
                           'replied_to_message_text': message.reply_to_message.text if message.reply_to_message else None,
                           'replied_to_message_id': message.reply_to_message.message_id if message.reply_to_message else None,
                           'replied_to_message_date': message.reply_to_message.date if message.reply_to_message else None
                           }
            db_example.insert_data('table_replies', data_for_db)
        else:
            print("Сообщение не является вопросом, заданным через бота")
    # replied_message_id = message.reply_to_message.message_id  # Айди сообщения, на которое ответили (основное сообщение)
    # reply_message_id = message.message_id  # Айди реплая


# Обработчик на колбэк инлайн кнопки
@router.callback_query(F.data == 'callback_question')
async def get_question(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Введите вопрос:')
    await state.update_data(msg=callback.message.message_id)
    await state.set_state(Ask_Question.question)
    await callback.answer()


# Удаление сообщения после нажатия
@router.callback_query(F.data == 'callback_delete')
async def delete_msg(callback: CallbackQuery):
    await callback.message.delete()
