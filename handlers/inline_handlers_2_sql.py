from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from database.database_sql import Database
from filters.chat_filters import ChatTypeFilter
from keyboards import inline_buttons

router = Router()


class About(StatesGroup):
    first_name = State()
    last_name = State()
    confirm = State()


class Question(StatesGroup):
    question = State()


# Регистрация в ЛС бота для авторизации в веб-приложении
@router.message(ChatTypeFilter(chat_type=["private"]), CommandStart())
async def command_private_registration_start(message: Message):
    await message.answer('Регистрация (ФИО), узнать свои данные и забыл пароль /start',
                         reply_markup=inline_buttons.private_kb)


# Получение имени
@router.message(About.first_name)
async def process_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await state.set_state(About.last_name)
    await message.answer("Введите свою фамилию:",
                         reply_markup=inline_buttons.delete_kb)


# Создаем дб с таблицей
db_example = Database("example.db")

# таблица с данными пользователей лс
columns_users_private = [('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                         ('user_id', 'INTEGER'),
                         ('password', 'TEXT'),
                         ('username', 'TEXT'),
                         ('user_first_name', 'TEXT'),
                         ('user_last_name', 'TEXT'),
                         ('date', 'INTEGER')]
db_example.create_table("table_users_private", columns_users_private)


# Получение фамилии и запись данных в бд
@router.message(About.last_name)
async def process_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await state.set_state(About.confirm)
    data = await state.get_data()
    data_for_db = {
        'user_id': message.from_user.id,
        'password': None,
        'username': message.from_user.username,
        'user_first_name': data["first_name"],
        'user_last_name': data["last_name"],
        'date': int(message.date.timestamp()),
    }
    # Попытка проверить, что пользователь существует
    if db_example.check_value("table_users_private", "user_id", message.from_user.id):
        db_example.insert_data("table_users_private", data_for_db)
        await message.answer(f'Спасибо, вы внесены в базу данных!'
                             f'\nВаш логин для регистрации в веб-приложении: {data_for_db["user_id"]}'
                             f'\nВаше ФИО: {data_for_db["user_first_name"]} {data_for_db["user_last_name"]}',
                             reply_markup=inline_buttons.thank_kb)
        await state.clear()
    else:
        print("Пользователь уже существует!")
        await message.answer(f'Вы уже внесены в базу данных.',
                             reply_markup=inline_buttons.my_data_kb)
        await state.clear()


# таблица с участниками чата
columns_users = [('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
                 ('chat_id', 'INTEGER'),
                 ('chat_username', 'TEXT'),
                 ('user_id', 'INTEGER'),
                 ('username', 'TEXT'),
                 ('user_first_name', 'TEXT'),
                 ('user_last_name', 'TEXT')]
db_example.create_table("table_users", columns_users)


# Запись участников группового чата в бд по команде start
@router.message(ChatTypeFilter(chat_type=["group"]), CommandStart())
async def command_group_registration_start(message: Message):
    # Добавляем пользователей в БД при нажатии /start
    data_for_db = {
        'chat_id': message.chat.id,
        'chat_username': message.chat.title,
        'user_id': message.from_user.id,
        'username': message.from_user.username,
        'user_first_name': message.from_user.first_name,
        'user_last_name': message.from_user.last_name
    }
    # Попытка проверить, что пользователь не существует
    if (db_example.check_value("table_users", "user_id", message.from_user.id)
            or db_example.check_value("table_users", "chat_id", message.chat.id)):
        db_example.insert_data("table_users", data_for_db)
        await message.answer(f'Спасибо, вы стали участником чата в веб-приложении, {message.from_user.username}!',
                             reply_markup=inline_buttons.thank_kb)
    else:
        print("Пользователь уже существует")


# Вызов сообщения с функционалом бота: задать вопрос и перейти на сайт
@router.message(ChatTypeFilter(chat_type=["group"]), Command('feature'))
async def command_feature(message: Message):
    await message.answer('Это основное сообщение тестирования команды /feature для вызова функций бота.',
                         reply_markup=inline_buttons.main_kb)


# Прототип хранения фото
# @router.message(ChatTypeFilter(chat_type=["group"]))
# async def get_photo(message: Message):
#     file_id = message.photo[-1].file_id # нужно где-то сохранить
#     await message.bot.send_photo(message.chat.id, file_id)
#     file_info = await message.bot.get_file(message.photo[-1].file_id)
#     await message.photo[-1].download(file_info.file_path.split('photos/')[1])


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
db_example.create_table("table_messages", columns_messages)


# Запись в бд отправленного вопроса пользователя
@router.message(ChatTypeFilter(chat_type=["group"]), Question.question)
async def process_asking_question(message: Message, state: FSMContext):
    await state.update_data(question=message.text)
    data = await state.get_data()  # ХРАНИТСЯ АЙДИ СООБЩЕНИЯ И ТЕКСТ СООБЩЕНИЯ
    print(data)
    data_for_db = {'message_id': message.message_id,
                   'chat_id': message.chat.id,
                   'user_id': message.from_user.id,
                   'message_text': message.text,
                   'chat_username': message.chat.title,
                   'username': message.from_user.username,
                   'date': int(message.date.timestamp()),
                   }
    if data["question"] == ".":
        await message.answer(f'Ваш вопрос не будет записан!',
                             reply_markup=inline_buttons.thank_kb)
        await state.clear()  # чтобы не засорялся, у пользователя слетало состояние
    else:
        if data["question"] is None:
            await message.answer(f'Бот на данный момент принимает вопросы только в текстовом виде.',
                                 reply_markup=inline_buttons.delete_kb)
            await state.clear()
        else:
            db_example.insert_data("table_messages", data_for_db)
            await message.answer(f'Спасибо, ваш вопрос принят!'
                                 f'\nВопрос задан: {message.from_user.id}'
                                 f'\nВаш вопрос: {data["question"]}',
                                 reply_markup=inline_buttons.thank_kb)
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
db_example.create_table("table_replies", columns_replies)


# Сохраняем только реплаи, которые были даны на вопросы при помощи бота
@router.message(ChatTypeFilter(chat_type=["group"]))
async def save_reply_from_process_message(message: Message):
    # Check if the message is a reply
    if message.reply_to_message:
        if message.text is None:
            await message.answer(f'Бот на данный момент принимает ответы только в текстовом виде.',
                                 reply_markup=inline_buttons.delete_kb)
        else:
            if not db_example.check_value("table_messages", "message_id", message.reply_to_message.message_id):
                data_for_db = {'message_id': message.message_id,
                               'chat_id': message.chat.id,
                               'user_id': message.from_user.id,
                               'message_text': message.text,
                               'chat_username': message.chat.title,
                               'username': message.from_user.username,
                               'date': int(message.date.timestamp()),
                               'replied_to_user_id': message.reply_to_message.from_user.id if message.reply_to_message else None,
                               'replied_to_message_text': message.reply_to_message.text if message.reply_to_message else None,
                               'replied_to_message_id': message.reply_to_message.message_id if message.reply_to_message else None,
                               'replied_to_message_date': int(
                                   message.reply_to_message.date.timestamp()) if message.reply_to_message else None
                               }
                db_example.insert_data("table_replies", data_for_db)
            else:
                print("Сообщение не является вопросом, заданным через бота")
    # replied_message_id = message.reply_to_message.message_id  # Айди сообщения, на которое ответили (основное сообщение)
    # reply_message_id = message.message_id  # Айди реплая


# Сделать для получения данный для sqlite3
@router.callback_query(F.data == 'callback_my_data')
async def get_data(callback: CallbackQuery):
    await callback.message.edit_text(f'Тут должны быть ваши данные\n'
                                     f'\nФИО: '
                                     f'{db_example.get_value("table_users_private", "user_first_name", callback.from_user.id)} '
                                     f'{db_example.get_value("table_users_private", "user_last_name", callback.from_user.id)}'
                                     f'\nВаш логин для веб-приложения: '
                                     f'{db_example.get_value("table_users_private", "user_id", callback.from_user.id)}',
                                     reply_markup=inline_buttons.thank_kb)
    await callback.answer()


# Обработчик на колбэк на регистрацию
@router.callback_query(F.data == 'callback_registration')
async def get_registration(callback: CallbackQuery, state: FSMContext):
    # Попытка проверить, что пользователь не существует
    if not db_example.check_value("table_users_private", "user_id", callback.from_user.id):
        await callback.message.edit_text(f'Вы уже внесены в базу данных.',
                                         reply_markup=inline_buttons.my_data_kb)
        await state.clear()
    else:
        await state.set_state(About.first_name)
        await callback.message.edit_text('Введите свое имя:',
                                         reply_markup=inline_buttons.delete_kb)


# Обработчик на колбэк инлайн кнопки отправки вопроса
@router.callback_query(F.data == 'callback_question')
async def get_question(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Для отмены ввода отправьте "."'
                                     '\nВведите вопрос:')
    await state.update_data(message=callback.message.message_id)
    await state.set_state(Question.question)
    await callback.answer()


# Удаление сообщения после нажатия для fsm
@router.callback_query(F.data == 'callback_delete')
async def get_delete_message(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await callback.message.delete()
    await state.clear()


# Удаление сообщения после нажатия обычных сообщений
@router.callback_query(F.data == 'callback_thank')
async def get_thank_message(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()


# Удаление профиля пользователя, когда он забыл пароль для восстановления
@router.callback_query(F.data == 'callback_password')
async def get_thank_message(callback: CallbackQuery):
    if db_example.delete_user('table_users_private', 'user_id', callback.from_user.id):
        await callback.message.edit_text('Ваша учетная запись была удалена из базы данных.'
                                         '\nМожете повторить вход в веб-приложение по логину и с новым паролем, '
                                         'после повторной регистрации через /start.',
                                         reply_markup=inline_buttons.thank_kb)
    else:
        await callback.message.edit_text('Вы не найдены в базе данных пользователей. Подтвердите свое участие в боте, '
                                         'отправив или выбрав команду /start',
                                         reply_markup=inline_buttons.thank_kb)
