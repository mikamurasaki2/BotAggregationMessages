from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

# from database.database_sql import Database
from filters.chat_filters import ChatTypeFilter
from keyboards import inline_buttons

from bot import bot
from database.database_mysql import *

router = Router()


class Ask_Question(StatesGroup):
    question = State()


# Внесение пользователь в таблицу для доступа регистрации в веб-приложении
@router.message(ChatTypeFilter(chat_type=["private"]), Command('registration'))
async def cmd_reg(message: Message):
    # Добавляем пользователей в БД при нажатии /registration
    data_for_db = {
        'user_id': message.from_user.id,
        'password': None,
        'username': message.from_user.username,
        'user_first_name': message.from_user.first_name,
        'user_last_name': message.from_user.last_name,
        'date': int(message.date.timestamp()),
    }
    # Попытка проверить, что пользователь не существует
    if not check_private_user(message.from_user.id):
        insert_private_user(data_for_db)
    else:
        print("Пользователь уже существует!")
    await message.answer(f'Спасибо, вы внесены в базу данных!'
                         f'\nВаш логин для регистрации в веб-приложении: {message.from_user.id}')


# Запись участников чата в таблицу по команде start
@router.message(ChatTypeFilter(chat_type=["group"]), Command('start'))
async def cmd_start(message: Message):
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
    if check_user(user_id=message.from_user.id, chat_id=message.chat.id):
        insert_user(data_for_db)
    else:
        print("Пользователь уже существует")


# Вызов сообщения с функционалом бота: задать вопрос и перейти на сайт
@router.message(ChatTypeFilter(chat_type=["group"]), Command('service'))
async def cmd_main(message: Message):
    await message.answer('Это основное сообщение тестирования команды /service для вызова функций бота.',
                         reply_markup=inline_buttons.main_kb)


# Прототип хранения фото
# @router.message(ChatTypeFilter(chat_type=["group"]))
# async def get_photo(message: Message):
#     file_id = message.photo[-1].file_id # нужно где-то сохранить
#     await message.bot.send_photo(message.chat.id, file_id)
#     file_info = await message.bot.get_file(message.photo[-1].file_id)
#     await message.photo[-1].download(file_info.file_path.split('photos/')[1])

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
                   'chat_username': message.chat.title,
                   'username': message.from_user.username,
                   'date': (message.date.timestamp()),
                   }
    if data["question"] == "-":
        await message.answer(f'Ваш вопрос не будет записан!',
                             reply_markup=inline_buttons.delete_kb)
        await state.clear()  # чтобы не засорялся, у пользователя слетало состояние
    else:
        if data["question"] is None:
            await message.answer(f'Бот на данный момент принимает вопросы только в текстовом виде.',
                                 reply_markup=inline_buttons.delete_kb)
            await state.clear()
        else:
            insert_message(data_for_db)
            await message.answer(f'Спасибо, ваш вопрос принят!'
                                 f'\nВопрос задан: {message.from_user.id}'
                                 f'\nВаш вопрос: {data["question"]}',
                                 reply_markup=inline_buttons.delete_kb)
            await state.clear()  # чтобы не засорялся, у пользователя слетало состояние



# Сохраняем только реплаи, которые были даны на вопросы через бот
@router.message(ChatTypeFilter(chat_type=["group"]))
async def process_message(message: Message):
    # Check if the message is a reply
    if message.reply_to_message:
        if message.text is None:
            await message.answer(f'Бот на данный момент принимает ответы только в текстовом виде.',
                                 reply_markup=inline_buttons.delete_kb)
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
                           'replied_to_message_date': int(message.reply_to_message.date.timestamp()) if message.reply_to_message else None
                           }
                insert_reply(data_for_db)
            else:
                print("Сообщение не является вопросом, заданным через бота")
    # replied_message_id = message.reply_to_message.message_id  # Айди сообщения, на которое ответили (основное сообщение)
    # reply_message_id = message.message_id  # Айди реплая


# Обработчик на колбэк инлайн кнопки
@router.callback_query(F.data == 'callback_question')
async def get_question(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Для отмены ввода введите -. \nВведите вопрос:')
    await state.update_data(msg=callback.message.message_id)
    await state.set_state(Ask_Question.question)
    await callback.answer()


# Удаление сообщения после нажатия
@router.callback_query(F.data == 'callback_delete')
async def delete_msg(callback: CallbackQuery):
    await callback.message.delete()

