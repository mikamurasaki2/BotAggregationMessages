# Создание двух инлайн кнопок
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Посмотреть доску с вопросами', url='31.129.96.68'),
     # url кнопка для веб-приложения
     InlineKeyboardButton(text='Задать вопрос', callback_data='callback_question_type')],
    [InlineKeyboardButton(text='Закрыть', callback_data='callback_thank')]
    # кнопка удаления сообщения после нажатия "Отмена"
])

question_type_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Теоретические вопросы', callback_data='callback_question_type_theory'),
     InlineKeyboardButton(text='Домашнее задание', callback_data='callback_question_type_homework'),
     InlineKeyboardButton(text='Общее', callback_data='callback_question_type_general')]
])


delete_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отмена', callback_data='callback_delete')]
    # кнопка удаления сообщения после нажатия "Отмена"
])

thank_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Спасибо', callback_data='callback_thank')]
    # кнопка удаления сообщения после нажатия "Спасибо"
])

my_data_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Мои данные', callback_data='callback_my_data')]
])

private_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Зарегистрироваться', callback_data='callback_registration'),
     InlineKeyboardButton(text='Узнать свои данные  для авторизации', callback_data='callback_my_data')],
    [InlineKeyboardButton(text='Забыл пароль', callback_data='callback_password')]
])
