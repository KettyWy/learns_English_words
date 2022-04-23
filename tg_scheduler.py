import os
from datetime import datetime
from time import sleep
from db_work import get_all_active_users, update_user
from tg import command_get_word

if __name__ == '__main__':
    while not os.path.exists('base.db'):
        sleep(5)

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

                command_get_word(user=user)
                update_user(user.id, **{'send_at': now(), 'answer_at': 0})

        sleep(1)
