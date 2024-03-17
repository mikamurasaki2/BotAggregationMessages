# Создание двух инлайн кнопок
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Посмотреть доску с вопросами', url='https://youtube.com'),
     # url кнопка для веб-приложения
     InlineKeyboardButton(text='Задать вопрос', callback_data='callback_question')],  # по идее кнопка для вызова fsm
    [InlineKeyboardButton(text='Закрыть', callback_data='callback_delete')]
    # кнопка удаления сообщения после нажатия "Отмена"
])

delete_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Спасибо', callback_data='callback_delete')]
    # кнопка удаления сообщения после нажатия "Спасибо"
])