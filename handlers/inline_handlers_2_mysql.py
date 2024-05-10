import hashlib

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
import bcrypt

from filters.chat_filters import ChatTypeFilter
from keyboards import inline_buttons
from database.database_mysql import *

router = Router()


class About(StatesGroup):
    first_name = State()
    last_name = State()
    password = State()
    confirm = State()


class Question(StatesGroup):
    question = State()


# Регистрация в ЛС бота для авторизации в веб-приложении
@router.message(ChatTypeFilter(chat_type=["private"]), CommandStart())
async def command_private_registration_start(message: Message):
    await message.answer('Регистрация (ФИО), узнать свои данные и забыл пароль /start',
                         reply_markup=inline_buttons.private_kb)
    await message.delete()


# Получение имени
@router.message(About.first_name)
async def process_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await state.set_state(About.last_name)
    await message.answer("Введите свою фамилию:")


# Получение фамилии
@router.message(About.last_name)
async def process_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await state.set_state(About.password)
    await message.answer("Введите пароль:")


# Получение фамилии и запись данных в бд
@router.message(About.password)
async def process_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    await state.set_state(About.confirm)
    data = await state.get_data()
    hashed_password = bcrypt.hashpw(data["password"].encode('utf-8'), bcrypt.gensalt())
    hashed_password_sha256 = hashlib.sha256(data["password"].encode()).hexdigest()
    data_for_db = {
        'user_id': message.from_user.id,
        'password': data["password"],  # hashed_password_sha256,
        'username': message.from_user.username,
        'user_first_name': data["first_name"],
        'user_last_name': data["last_name"],
        'date': int(message.date.timestamp()),
        'is_admin': 0
    }
    await message.delete()
    print(data)
    # Попытка проверить, что пользователь существует
    if not check_private_user(message.from_user.id):
        insert_private_user(data_for_db)
        await message.answer(f'Спасибо, вы внесены в базу данных!'
                             f'\nВаш логин для регистрации в веб-приложении: {data_for_db["user_id"]}'
                             f'\nВаше ФИО: {data_for_db["user_first_name"]} {data_for_db["user_last_name"]}')
        await state.clear()
    else:
        await message.answer(f'Вы уже внесены в базу данных.',
                             reply_markup=inline_buttons.my_data_kb)
        await state.clear()


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
        'user_last_name': message.from_user.last_name,
        'is_admin': 0
    }
    # Попытка проверить, что пользователь не существует
    if check_user(user_id=message.from_user.id, chat_id=message.chat.id):
        insert_user(data_for_db)
        await message.answer(f'Спасибо, вы стали участником чата в веб-приложении, {message.from_user.username}!',
                             reply_markup=inline_buttons.thank_kb)
        await message.delete()
    else:
        await message.delete()


# Вызов сообщения с функционалом бота: задать вопрос и перейти на сайт
@router.message(ChatTypeFilter(chat_type=["group"]), Command('feature'))
async def command_feature(message: Message):
    await message.answer('Это основное сообщение тестирования команды /feature для вызова функций бота.',
                         reply_markup=inline_buttons.main_kb)
    await message.delete()


# Прототип хранения фото
# @router.message(ChatTypeFilter(chat_type=["group"]))
# async def get_photo(message: Message):
#     file_id = message.photo[-1].file_id # нужно где-то сохранить
#     await message.bot.send_photo(message.chat.id, file_id)
#     file_info = await message.bot.get_file(message.photo[-1].file_id)
#     await message.photo[-1].download(file_info.file_path.split('photos/')[1])


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
                   'question_type': str(data["question_type"])
                   }

    if data["question"] is None:
        await message.answer(f'Бот на данный момент принимает вопросы только в текстовом виде.',
                             reply_markup=inline_buttons.thank_kb)
        await state.clear()
    else:
        insert_message(data_for_db)
        await message.answer(f'Спасибо, ваш вопрос принят!'
                             f'\nВопрос задан: {message.from_user.id}'
                             f'\nВаш вопрос: {data["question"]}',
                             reply_markup=inline_buttons.thank_kb)
        await state.clear()  # чтобы не засорялся, у пользователя слетало состояние


# Сохраняем только реплаи, которые были даны на вопросы через бота
@router.message(ChatTypeFilter(chat_type=["group"]))
async def save_reply_from_process_message(message: Message):
    # Check if the message is a reply
    if message.reply_to_message:
        if message.text is None:
            await message.answer(f'Бот на данный момент принимает ответы только в текстовом виде.',
                                 reply_markup=inline_buttons.thank_kb)
        else:
            if check_message(message.reply_to_message.message_id):
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
                                   message.reply_to_message.date.timestamp()) if message.reply_to_message else None,
                               'post_id': message.reply_to_message.message_id
                               }
                insert_reply(data_for_db)


# Сделать get в db и доделать
@router.callback_query(F.data == 'callback_my_data')
async def get_data(callback: CallbackQuery, state: FSMContext):
    if check_private_user(callback.from_user.id):
        await callback.message.edit_text(f'Тут должны быть ваши данные\n'
                                         f'\nФИО: {get_last_name(callback.from_user.id)} {get_first_name(callback.from_user.id)}'
                                         f'\nВаш логин для веб-приложения: {get_user_id(callback.from_user.id)}',
                                         reply_markup=inline_buttons.thank_kb)
        await callback.answer()
    else:
        await callback.message.edit_text(f'Вы еще не внесены в базу данных приложения. '
                                         f'Пожалуйста, выберите команду /start',
                                         reply_markup=inline_buttons.thank_kb)
        await callback.answer()


# Обработчик на колбэк на регистрацию
@router.callback_query(F.data == 'callback_registration')
async def get_registration(callback: CallbackQuery, state: FSMContext):
    # Попытка проверить, что пользователь не существует
    if check_private_user(callback.from_user.id):
        await callback.message.edit_text(f'Вы уже внесены в базу данных.',
                                         reply_markup=inline_buttons.my_data_kb)
        await state.clear()
    else:
        await state.set_state(About.first_name)
        await callback.message.edit_text('Введите свое имя:')


# Обработчик на колбэк инлайн кнопки
@router.callback_query(F.data == 'callback_question_type')
async def get_question_type_general(callback: CallbackQuery):
    await callback.message.edit_text('Выберите тип вопроса:',
                                     reply_markup=inline_buttons.question_type_kb)
    await callback.answer()


@router.callback_query(F.data == 'callback_question_type_general')
async def get_question_type_general(callback: CallbackQuery, state: FSMContext):
    await state.update_data(question_type='Общее')
    await callback.message.edit_text('Введите вопрос:',
                                     reply_markup=inline_buttons.delete_kb)
    await state.update_data(message=callback.message.message_id)
    await state.set_state(Question.question)
    await callback.answer()


@router.callback_query(F.data == 'callback_question_type_theory')
async def get_question_type_theory(callback: CallbackQuery, state: FSMContext):
    await state.update_data(question_type='Теоретические вопросы')
    await callback.message.edit_text('Введите вопрос:',
                                     reply_markup=inline_buttons.delete_kb)
    await state.update_data(message=callback.message.message_id)
    await state.set_state(Question.question)
    await callback.answer()


@router.callback_query(F.data == 'callback_question_type_homework')
async def get_question_type_homework(callback: CallbackQuery, state: FSMContext):
    await state.update_data(question_type='Домашнее задание')
    await callback.message.edit_text('Введите вопрос:',
                                     reply_markup=inline_buttons.delete_kb)
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
async def get_thank_message(callback: CallbackQuery, state: FSMContext):
    if delete_user(callback.from_user.id):
        await callback.message.edit_text('Ваша учетная запись была удалена из базы данных.'
                                         '\nМожете повторить вход в веб-приложение по логину и с новым паролем, '
                                         'после повторной регистрации через /start.',
                                         reply_markup=inline_buttons.thank_kb)
    else:
        await callback.message.edit_text('Вы не найдены в базе данных пользователей. Подтвердите свое участие в боте, '
                                         'отправив или выбрав команду /start',
                                         reply_markup=inline_buttons.thank_kb)
