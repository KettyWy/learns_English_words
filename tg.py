from datetime import datetime
import random
from os import getenv
from dotenv import load_dotenv
import telebot
from telebot import types
from db_work import *

load_dotenv()
TOKEN = getenv('TOKEN')
ADMIN_CHAT_ID = getenv('ADMIN_CHAT_ID')
MODES = {
    1: 'Слово => Перевод',
    2: 'Перевод => Слово',
}
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')


def _delete_word(message):
    """
    Удаление слова

    :param message:
    :return:
    """
    word = message.text
    user = get_user(message.chat.id)
    row = delete_word(user.id, word)
    if row:
        bot.reply_to(message, f'Слово {word} удалено')
    else:
        bot.reply_to(message, f'Слово {word} не найдено')


def _add_word(message):
    """
    Добавление нового слова

    :param message:
    :return:
    """
    user = get_user(message.chat.id)
    texts = []
    if '\n' in message.text:
        texts = message.text.split('\n')
    else:
        texts.append(message.text)
    try:
        for text in texts:
            if not text:
                continue

            word, translate, transcript = text.split('*')
            if not word or not translate:
                raise ValueError

            try:
                create_word(user.id, word, translate, transcript)
                bot.reply_to(message, f'Слово {word} добавлено')
            except IntegrityError:
                bot.reply_to(message, f'Слово {word} уже существует')

    except ValueError:
        bot.reply_to(message, f'Неверный формат. Необходимо вводить в формате <b>Слово*Перевод*Транскрипт</b>. Слово и перевод обязательны, как произносится не обязательно, но <b>*</b> должна все равно стоять')
        return


def _edit_sleep(message):
    """
    Изменить интервал отправки слов по расписанию

    :param message:
    :return:
    """
    user = get_user(message.chat.id)
    try:
        time = int(message.text)
    except ValueError:
        bot.reply_to(message, 'Только целочисленное значение в минутах')
        return
    change_time_to_sleep(user.id, time)
    bot.reply_to(message, 'Готово!')


def _edit_options_num(message):
    """
    Изменить количество вариантов ответа

    :param message:
    :return:
    """
    user = get_user(message.chat.id)
    try:
        kwargs = {
            'options_num': int(message.text),
        }
    except ValueError:
        bot.reply_to(message, 'Нужно указать циферку')
        return
    update_user(user.id, **kwargs)
    bot.reply_to(message, 'Готово!')


def _find_word(message):
    """
    Найти слово

    :param message:
    :return:
    """
    user = get_user(message.chat.id)
    word = get_word(user.id, message.text)
    if not word:
        bot.reply_to(message, f'Слово {message.text} не найдено.')
        return
    bot.reply_to(message, f'{word.word} - {word.translate} - {word.transcript}')


def _get_all_word_objs(user_id):
    """
    Получение всех слов пользователя, разбивка их по листам

    :param user_id: id
    :return: weights, words, translates, transcripts
    """
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


def _get_word(user, mode=1, options_num=4):
    """
    Получение случайного слова, учитывая веса слов

    :param user: Users
    :param mode: 1 - прямой перевод
                 2 - обратный перевод
    :param options_num: количество вариантов ответа
    :return: word, translations, transcript
    """
    weights, words, translates, transcripts = _get_all_word_objs(user.id)

    def mode_1(weights=weights, words=words, translates=translates):
        word = random.choices(words, weights=weights)[0]
        translations = set()
        word_from_db = get_word(user.id, word)
        translations.add(word_from_db.translate)
        while len(translations) != options_num:
            translations.add(random.choice(translates))
        return word, translations, word_from_db.transcript

    def mode_2(weights=weights, words=words, translates=translates):
        word = random.choices(translates, weights=weights)[0]
        translations = set()
        word_from_db = get_word(user.id, word)
        translations.add(word_from_db.word)
        while len(translations) != options_num:
            translations.add(random.choice(words))
        return word, translations, ''

    if len(words) < options_num:
        bot.send_message(user.chat_id, f'Рановато, необходимо внести слов: {options_num}')
        return

    modes = {
        1: mode_1,
        2: mode_2,
    }

    return modes[mode]()


def _get_inline_markup(buttons: dict):
    """
    Формирование инлайн кнопок с вариантами ответа

    :param buttons: dict{button_text: callback_data}
    :return: markup
    """
    markup = types.InlineKeyboardMarkup()
    btns = []
    for text, callback_data in buttons.items():
        btns.append(types.InlineKeyboardButton(text, callback_data=callback_data))
    markup.add(*btns, row_width=2)
    return markup


def _send_review(message):
    """
    Пересылка сообщения (отзыва) администратору

    :param message:
    :return: None
    """
    bot.send_message(ADMIN_CHAT_ID, f'Отзыв от пользователя {message.chat.id}\n{message.html_text}')
    bot.reply_to(message, 'Благодарю за твое мнение.')


def _export_words(user, path='export'):
    file_name = os.path.join(path, f'{str(user.chat_id)}.txt')
    if not os.path.exists(path):
        os.makedirs(path.replace('\\', '/'))
    weights, words, translates, transcripts = _get_all_word_objs(user.id)
    with open(f'{file_name}', 'w', encoding='utf-8') as f:
        for idx in range(len(words)):
            f.write(f'{words[idx]}*{translates[idx]}*{transcripts[idx]}\n')
    return f.name


@bot.message_handler(commands=['start'])
def command_start(message):
    user = get_user(message.chat.id)
    if not user:
        create_user(message.chat.id)
        bot.send_message(ADMIN_CHAT_ID, 'New user')
    bot.send_message(message.chat.id, """
Привет, друг!
Меня зовут Вордик, я помогу тебе выучить слова.

Для начала пришли мне слова, которые хочешь запомнить (минимум 4), для этого отправь команду /add_word

Если ты ошибся при вводе, можешь удалить слово командой /delete_word и прислать исправленное /add_word

Забыл перевод? Воспользуйся командой /find_word и я пришлю тебе нужное слово

Готов к тренеровке? Воспользуйся командой /edit_timeout и пришли мне через сколько минут тебе присылать новое слово.
Если хочешь получать новые слова без задержки пришли -1, если не хочешь получать новые слова пришли 0 или не отвечай на последнее слово, пока ты не ответишь я не буду тебя беспокоить.
Получить случайное слово в ручном режиме - /get_word

Изменить режим - /edit_mode

Изменить количество вариантов ответа - /options_num

Если хочешь сохранить введенные слова у себя (чтоб загрузить их, если что-то случится), воспользуйся командой /export_words.

Все эти команды, при необходимости, можешь найти в меню рядом со строкой ввода сообщения.

Рад познакомиться, надеюсь на плодотворное сотрудничество.

P.S.: Обязательно пришли мне свое мнение или пожелание, воспользовавшись командой /review
""")


@bot.message_handler(commands=['delete_word'])
def command_delete_word(message):
    markup = types.ForceReply(selective=False)
    bot.reply_to(message, "Удалить слово.\nКакое слово хотите удалить?", reply_markup=markup)


@bot.message_handler(commands=['add_word'])
def command_add_word(message):
    markup = types.ForceReply(selective=False)
    bot.reply_to(message, "Добавить слово.\nВведи слово в формате <b>Слово*Перевод*Как произносится</b>. Можно ввести сразу несколько слов. Каждое слово с новой строки", reply_markup=markup)


@bot.message_handler(commands=['edit_timeout'])
def command_edit_timeout(message):
    markup = types.ForceReply(selective=False)
    bot.reply_to(message, "Изменить интервал.\nКакой интервал (в минутах) между отправкой слов?", reply_markup=markup)


@bot.message_handler(commands=['get_word'])
def command_get_word(message=None, user=None):
    buttons = {}
    if not user:
        user = get_user(message.chat.id)
    word, translations, transcript = _get_word(user, user.mode, user.options_num)
    for translate in translations:
        buttons[translate] = f'{word}={translate}'
    markup = _get_inline_markup(buttons)
    bot.send_message(user.chat_id, f'Как переводится слово <b>{word}{f" ({transcript})" if transcript else ""}</b>?', reply_markup=markup)


@bot.message_handler(commands=['find_word'])
def command_add_word(message):
    markup = types.ForceReply(selective=False)
    bot.reply_to(message, "Найти слово.\nКакое слово найти?", reply_markup=markup)


@bot.message_handler(commands=['edit_mode'])
def command_add_word(message):
    buttons = {}
    for num, mode in MODES.items():
        buttons[mode] = f'edit_mode={num}'
    markup = _get_inline_markup(buttons)
    bot.send_message(message.chat.id, f'Выбери режим', reply_markup=markup)


@bot.message_handler(commands=['test'])
def test(message):
    markup = types.ForceReply(selective=False)
    bot.reply_to(message, "Изменить количество вариантов.\nСколько вариантов ответа хочешь получать?", reply_markup=markup)


@bot.message_handler(commands=['options_num'])
def test(message):
    markup = types.ForceReply(selective=False)
    bot.reply_to(message, "Изменить количество вариантов.\nСколько вариантов ответа хочешь получать?", reply_markup=markup)


@bot.message_handler(commands=['review'])
def review(message):
    markup = types.ForceReply(selective=False)
    bot.reply_to(message, "Отправить отзыв.\nМне очень важно твое мнение. Пришли мне свое мнение или пожелание.", reply_markup=markup)


@bot.message_handler(commands=['export_words'])
def review(message):
    user = get_user(message.chat.id)
    file = _export_words(user)
    bot.send_document(message.chat.id, open(file, 'r', encoding='utf-8'), visible_file_name='export.txt')


ARRAY_FUNCTIONS = {
    'Удалить слово': _delete_word,
    'Добавить слово': _add_word,
    'Изменить интервал': _edit_sleep,
    'Найти слово': _find_word,
    'Отправить отзыв': _send_review,
    'Изменить количество вариантов': _edit_options_num,
}


@bot.callback_query_handler(lambda message: True if message.data.split('=')[0] == 'edit_mode' else False)
def edit_mode_call_back(message):
    user_id = get_user(message.message.chat.id)
    kwargs = {
        'mode': int(message.data.split('=')[1]),
    }
    update_user(user_id, **kwargs)
    bot.edit_message_text(f'Установлен режим <b>{MODES[kwargs["mode"]]}</b>', message.message.chat.id, message.message.id)


@bot.callback_query_handler(lambda x: True)
def call_back(message):
    user_id = get_user(message.message.chat.id)
    word, answer = message.data.split('=')
    word_from_db = get_word(user_id, word)
    text = message.message.html_text
    if word_from_db.translate == answer or word_from_db.word == answer:
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
