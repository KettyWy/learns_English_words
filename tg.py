from datetime import datetime
import random
from os import getenv
from dotenv import load_dotenv
import telebot
from telebot import types
from db_work import *

load_dotenv()
TOKEN = getenv('TOKEN')
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')


def _delete_word(message):
    word = message.text
    user = get_user(message.chat.id)
    row = delete_word(user.id, word)
    if row:
        bot.reply_to(message, f'Слово {word} удалено')
    else:
        bot.reply_to(message, f'Слово {word} не найдено')


def _add_word(message):
    user = get_user(message.chat.id)
    text = []
    if '\n' in message.text:
        text = message.text.split('\n')
    else:
        text.append(message.text)
    try:
        for word in text:
            word, translate, transcript = word.split('*')
            if not word or not translate:
                raise ValueError

            try:
                create_word(user.id, word, translate, transcript)
                bot.reply_to(message, f'Слово {word} добавлено')
            except IntegrityError:
                bot.reply_to(message, f'Слово {word} уже существует')

    except ValueError:
        bot.reply_to(message, f'Неверный формат. Необходимо вводить в формате <b>Слово*Перевод*Транскрипт</b>. Слово и перевод обязательны, транскрипт не обязателен, но <b>*</b> должна все равно стоять')
        return


def _edit_sleep(message):
    user = get_user(message.chat.id)
    try:
        time = int(message.text)
    except ValueError:
        bot.reply_to(message, 'Только целочисленное значение в минутах')
        return
    change_time_to_sleep(user.id, time)
    bot.reply_to(message, 'Готово!')


def _find_word(message):
    user = get_user(message.chat.id)
    word = get_word(user.id, message.text)
    if not word:
        bot.reply_to(message, f'Слово {message.text} не найдено.')
        return
    bot.reply_to(message, f'{word.word} - {word.translate} - {word.transcript}')


def _get_all_word_objs(user_id):
    words = []
    weights = []
    translates = []
    transcripts = []
    word_objs = get_all_words_for_user(user_id)
    for word_obj in word_objs:
        words.append(word_obj.word)
        weights.append(word_obj.weight)
        translates.append(word_obj.translate)
        transcripts.append(word_obj.transcript)

    return weights, words, translates, transcripts


def _get_word(user):
    # user = get_user(message.chat.id)
    weights, words, translates, transcripts = _get_all_word_objs(user.id)
    if len(words) < 4:
        bot.send_message(user.chat_id, 'Рановато, заполни минимум 4 слова')
        return
    word = random.choices(words, weights=weights)[0]
    translations = set()
    word = get_word(user.id, word)
    translations.add(word.translate)
    while len(translations) != 4:
        translations.add(random.choice(translates))
    return word.word, translations, word.transcript


def _get_inline_markup(buttons: dict):
    markup = types.InlineKeyboardMarkup()
    btns = []
    for text, callback_data in buttons.items():
        btns.append(types.InlineKeyboardButton(text, callback_data=callback_data))
    markup.add(*btns, row_width=2)
    return markup


@bot.message_handler(commands=['start'])
def command_start(message):
    user = get_user(message.chat.id)
    if not user:
        create_user(message.chat.id)


@bot.message_handler(commands=['delete_word'])
def command_delete_word(message):
    markup = types.ForceReply(selective=False)
    bot.reply_to(message, "Удалить слово.\nКакое слово хотите удалить?", reply_markup=markup)


@bot.message_handler(commands=['add_word'])
def command_add_word(message):
    markup = types.ForceReply(selective=False)
    bot.reply_to(message, "Добавить слово.\nВведите слово в формате <b>Слово*Перевод*Транскрипт</b>. Можно ввести сразу несколько слов. Каждое слово с новой строки", reply_markup=markup)


@bot.message_handler(commands=['edit_timeout'])
def command_add_word(message):
    markup = types.ForceReply(selective=False)
    bot.reply_to(message, "Изменить интервал.\nКакой интервал (в минутах) между отправкой слов?", reply_markup=markup)


@bot.message_handler(commands=['get_word'])
def command_get_word(message):
    buttons = {}
    user = get_user(message.chat.id)
    word, translations, transcript = _get_word(user)
    for translate in translations:
        buttons[translate] = f'{word}={translate}'
    markup = _get_inline_markup(buttons)
    bot.send_message(message.chat.id, f'Как переводится слово <b>{word}{f" ({transcript})" if transcript else ""}</b>?', reply_markup=markup)


@bot.message_handler(commands=['find_word'])
def command_add_word(message):
    markup = types.ForceReply(selective=False)
    bot.reply_to(message, "Найти слово.\nКакое слово найти?", reply_markup=markup)


@bot.message_handler(commands=['test'])
def command_add_word(message):
    buttons = {
        'Текст 1': 'Data1',
        'Текст 2': 'Data2',
        'Текст 3': 'Data3',
        'Текст 4': 'Data4',
        'Текст 5': 'Data5',
    }
    btns = []
    for btn in ARRAY_FUNCTIONS:
        btns.append(types.KeyboardButton(btn))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(*btns)
    bot.reply_to(message, "Найти слово.\nКакое слово найти?", reply_markup=markup)


ARRAY_FUNCTIONS = {
    'Удалить слово': _delete_word,
    'Добавить слово': _add_word,
    'Изменить интервал': _edit_sleep,
    'Найти слово': _find_word,
}


@bot.callback_query_handler(lambda x: True)
def call_back(message):
    user_id = get_user(message.message.chat.id)
    word, answer = message.data.split('=')
    word_from_db = get_word(user_id, word)
    text = message.message.html_text
    if word_from_db.translate == answer:
        update_word(user_id, word, **{'weight': word_from_db.weight - 1})
        bot.edit_message_text(f'{text}\n<b>✅ Правильно</b>', message.message.chat.id, message.message.id)
    else:
        update_word(user_id, word, **{'weight': word_from_db.weight + 1})
        bot.edit_message_text(f'{text}\n<b>🚫 Не правильно</b>', message.message.chat.id, message.message.id)
    update_user(user_id, **{'answer_at': datetime.now()})


@bot.message_handler(func=lambda message: message.reply_to_message)
def reply_message(message):
    for command in ARRAY_FUNCTIONS:
        if message.reply_to_message.text.startswith(command):
            ARRAY_FUNCTIONS[command](message)


if __name__ == '__main__':
    bot.infinity_polling()
