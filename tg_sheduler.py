from datetime import datetime
from time import sleep
from db_work import get_all_active_users, update_user
from tg import bot, _get_word, _get_inline_markup


now = datetime.now


while True:
    users = get_all_active_users()
    for user in users:
        if not user.send_at.second and not user.answer_at.second or \
                (
                    (now() - user.send_at).total_seconds() > user.sleep * 60 and
                    user.answer_at.second and
                    (now() - user.answer_at).total_seconds() > user.sleep * 60
                ):

            buttons = {}
            word, translations, transcript = _get_word(user)
            for translate in translations:
                buttons[translate] = f'{word}={translate}'
            markup = _get_inline_markup(buttons)
            bot.send_message(user.chat_id,
                             f'Как переводится слово <b>{word}{f" ({transcript})" if transcript else ""}</b>?',
                             reply_markup=markup)
            update_user(user.id, **{'send_at': now(), 'answer_at': 0})

    sleep(1)
