from hashlib import sha256

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

import asyncio

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


def do_hash(password):
    """
    Функция хэширования пароля
    """
    return sha256(password.encode('utf-8')).hexdigest()


def get_time(time):
    """
    Функция преобразования времени по Мск
    """
    return int(time.utcnow().timestamp() + 3 * 60 * 60)


async def reset_fsm_state(user_id, state, timeout=30):
    """
    Функция сброса состояния после истечения времени в секундах
    """
    last_message_time = state.get('last_message_time')
    if last_message_time is None:
        # First message, save the time
        state['last_message_time'] = asyncio.get_running_loop().time()
        return

    current_time = asyncio.get_running_loop().time()
    time_since_last_message = current_time - last_message_time
    if time_since_last_message > timeout:
        # User has not written a new message within 5 minutes, reset the state
        state.reset_state()
        state['last_message_time'] = current_time


@router.message(ChatTypeFilter(chat_type=["private"]), CommandStart())
async def command_private_registration_start(message: Message):
    """
    Функция команды private для личного чата с ботом
    """
    await message.answer('Регистрация (ФИО), узнать свои данные и забыл пароль /start',
                         reply_markup=inline_buttons.private_kb)
    await message.delete()


@router.message(About.first_name)
async def process_first_name(message: Message, state: FSMContext):
    """
    Функция для получения ввода имени пользователя
    """
    await state.update_data(first_name=message.text)
    await state.set_state(About.last_name)
    await message.answer("Введите свою фамилию:")


# Получение фамилии
@router.message(About.last_name)
async def process_last_name(message: Message, state: FSMContext):
    """
    Функция для получения ввода фамилии пользователя
    """
    await state.update_data(last_name=message.text)
    await state.set_state(About.password)
    await message.answer("Введите пароль:")


# Получение фамилии и запись данных в бд
@router.message(About.password)
async def process_password(message: Message, state: FSMContext):
    """
    Функция получения ввода пароля пользователя и запись полученных данных в бд
    """
    await state.update_data(password=message.text)
    await state.set_state(About.confirm)
    data = await state.get_data()
    data_for_db = {
        'user_id': message.from_user.id,
        'password': do_hash(data["password"]),
        'username': message.from_user.username,
        'user_first_name': data["first_name"],
        'user_last_name': data["last_name"],
        'date': get_time(message.date),
        'is_admin': 0
    }
    await message.delete()
    print(data)
    # Проверка, что данный пользователь не существует
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


@router.message(ChatTypeFilter(chat_type=["group"]), CommandStart())
async def command_group_registration_start(message: Message):
    """
    Становление участником группового чата для использования веб-приложения.
    Автоматическое добавление пользователя по команде start.
    """
    data_for_db = {
        'chat_id': message.chat.id,
        'chat_username': message.chat.title,
        'user_id': message.from_user.id,
        'username': message.from_user.username,
        'user_first_name': message.from_user.first_name,
        'user_last_name': message.from_user.last_name,
        'is_admin': 0
    }
    # Проверка, что пользователь не существует
    if check_user(user_id=message.from_user.id, chat_id=message.chat.id):
        insert_user(data_for_db)
        await message.answer(f'Спасибо, вы стали участником чата в веб-приложении, {message.from_user.username}!',
                             reply_markup=inline_buttons.thank_kb)
        await message.delete()
    else:
        await message.delete()


@router.message(ChatTypeFilter(chat_type=["group"]), Command('feature'))
async def command_feature(message: Message):
    """
    Вызов сообщения по команде feаture для групповых чатов с выбором
    основных функций бота: задать вопрос и переход в веб-приложение по url-ссылке.
    """
    await message.answer('Это основное сообщение тестирования команды /feature для вызова функций бота.',
                         reply_markup=inline_buttons.main_kb)
    await message.delete()


# Запись в бд отправленного вопроса пользователя
@router.message(ChatTypeFilter(chat_type=["group"]), Question.question)
async def process_asking_question(message: Message, state: FSMContext):
    """
    Запись полученного вопроса в базу данных
    """
    await state.update_data(question=message.text)
    # Хранение полученных от ввода данных
    data = await state.get_data()
    print(data)
    data_for_db = {'message_id': message.message_id,
                   'chat_id': message.chat.id,
                   'user_id': message.from_user.id,
                   'message_text': message.text,
                   'chat_username': message.chat.title,
                   'username': message.from_user.username,
                   'date': get_time(message.date),
                   'question_type': str(data["question_type"]),
                   'is_admin_answer': 0
                   }
    # Проверка, что введенный вопрос - текстовое сообщение
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
        # Очистка состояния FSM
        await state.clear()


@router.message(ChatTypeFilter(chat_type=["group"]))
async def save_reply_from_process_message(message: Message):
    """
    Функция записи в бд ответного сообщения на вопрос, отправленный при помощи бота
    """
    # Проверка, что обрабатываемое сообщение является реплаем
    if message.reply_to_message:
        if message.text is None:
            await message.answer(f'Бот на данный момент принимает ответы только в текстовом виде.',
                                 reply_markup=inline_buttons.thank_kb)
        else:
            # Проверка, что это ответное сообщение на вопрос из бд
            if check_message(message.reply_to_message.message_id):
                # Проверка регистрации пользователя
                if not check_private_user(message.from_user.id):
                    data_anon = {
                        'user_id': message.from_user.id,
                        'password': None,
                        'username': message.from_user.username,
                        'user_first_name': message.from_user.first_name,
                        'user_last_name': message.from_user.last_name,
                        'date': get_time(message.date),
                        'is_admin': 0
                    }
                    insert_anon_private_user(data_anon)
                # Проверка, что это ответное сообщение от админа
                if check_reply_is_admin(message.from_user.id):
                    edit_message_have_admin_answer(message.reply_to_message.message_id, message.chat.id)
                data_for_db = {'message_id': message.message_id,
                               'chat_id': message.chat.id,
                               'user_id': message.from_user.id,
                               'message_text': message.text,
                               'chat_username': message.chat.title,
                               'username': message.from_user.username,
                               'date': get_time(message.date),
                               'replied_to_user_id': message.reply_to_message.from_user.id if message.reply_to_message else None,
                               'replied_to_message_text': message.reply_to_message.text if message.reply_to_message else None,
                               'replied_to_message_id': message.reply_to_message.message_id if message.reply_to_message else None,
                               'replied_to_message_date': get_time(
                                   message.reply_to_message.date) if message.reply_to_message else None,
                               'post_id': message.reply_to_message.message_id
                               }
                insert_reply(data_for_db)


# CALLBACKS

@router.callback_query(F.data == 'callback_my_data')
async def get_data(callback: CallbackQuery):
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


# Обработчик коллбэка на регистрацию
@router.callback_query(F.data == 'callback_registration')
async def get_registration(callback: CallbackQuery, state: FSMContext):
    # Проверка, что пользователь не существует
    if check_private_user(callback.from_user.id):
        await callback.message.edit_text(f'Вы уже внесены в базу данных.',
                                         reply_markup=inline_buttons.my_data_kb)
        await state.clear()
    else:
        await state.set_state(About.first_name)
        await callback.message.edit_text('Введите свое имя:')


@router.callback_query(F.data == 'callback_question_type')
async def get_question_type_general(callback: CallbackQuery):
    """
    Функция обработки коллбэка на инлайн кнопку для выбора категории вопроса
    """
    await callback.message.edit_text('Выберите тип вопроса:',
                                     reply_markup=inline_buttons.question_type_kb)
    await callback.answer()


@router.callback_query(F.data == 'callback_question_type_general')
async def get_question_type_general(callback: CallbackQuery, state: FSMContext):
    """
    Функция обработки коллбэка на категорию вопроса "Общее"
    И начало FSM для получения введенного вопроса
    """
    await state.update_data(question_type='Общее')
    await callback.message.edit_text('Введите вопрос:',
                                     reply_markup=inline_buttons.delete_kb)
    await state.update_data(message=callback.message.message_id)
    await state.set_state(Question.question)
    await reset_fsm_state(callback.from_user.id, Question.question)
    await callback.answer()


@router.callback_query(F.data == 'callback_question_type_theory')
async def get_question_type_theory(callback: CallbackQuery, state: FSMContext):
    """
    Функция обработки коллбэка на категорию вопроса "Теоретические вопросы"
    И начало FSM для получения введенного вопроса
    """
    await state.update_data(question_type='Теоретические вопросы')
    await callback.message.edit_text('Введите вопрос:',
                                     reply_markup=inline_buttons.delete_kb)
    await state.update_data(message=callback.message.message_id)
    await state.set_state(Question.question)
    await callback.answer()


@router.callback_query(F.data == 'callback_question_type_homework')
async def get_question_type_homework(callback: CallbackQuery, state: FSMContext):
    """
    Функция обработки коллбэка на категорию вопроса "Домашнее задание".
    И начало FSM для получения введенного вопроса
    """
    await state.update_data(question_type='Домашнее задание')
    await callback.message.edit_text('Введите вопрос:',
                                     reply_markup=inline_buttons.delete_kb)
    await state.update_data(message=callback.message.message_id)
    await state.set_state(Question.question)
    await callback.answer()


@router.callback_query(F.data == 'callback_delete')
async def get_delete_message(callback: CallbackQuery, state: FSMContext):
    """
    Функция обработчика коллбэка для прерывания состояния FSM ввода вопроса
    """
    current_state = await state.get_state()
    if current_state is None:
        return
    await callback.message.delete()
    await state.clear()


@router.callback_query(F.data == 'callback_thank')
async def get_thank_message(callback: CallbackQuery, state: FSMContext):
    """
    Функция обработки коллбэка для удаления обычных сообщений бота по кнопке
    """
    await callback.message.delete()
    await state.clear()


@router.callback_query(F.data == 'callback_password')
async def get_thank_message(callback: CallbackQuery):
    """
    Функция обработки коллбэка инлайн-кнопки для удаления профиля пользователя в бд
    """
    if delete_user(callback.from_user.id):
        await callback.message.edit_text('Ваша учетная запись была удалена из базы данных.'
                                         '\nМожете повторить вход в веб-приложение по логину и с новым паролем, '
                                         'после повторной регистрации через /start.',
                                         reply_markup=inline_buttons.thank_kb)
    else:
        await callback.message.edit_text('Вы не найдены в базе данных пользователей. Подтвердите свое участие в боте, '
                                         'отправив или выбрав команду /start',
                                         reply_markup=inline_buttons.thank_kb)
