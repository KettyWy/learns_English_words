import os

from models import *


def create_user(chat_id):
    row = Users(chat_id=chat_id)
    return row.save()


def get_user(chat_id):
    try:
        return Users.select().where(Users.chat_id == chat_id).get()
    except DoesNotExist:
        return False


def update_user(user_id, **kwarg):
    return Users.update(**kwarg).where(Users.id == user_id).execute()


def get_word(user_id, word):
    try:
        return Words.select().where(Words.user_id == user_id, Words.word == word).get()
    except DoesNotExist:
        return False


def change_time_to_sleep(user_id, time):
    return Users.update(sleep=time).where(Users.id == user_id).execute()


def create_word(user_id, word, translate, transcript):
    row = Words(
        user_id=user_id,
        word=word,
        translate=translate,
        transcript=transcript,
    )
    return row.save()


def update_word(user_id, word, **kwarg):
    return Words.update(**kwarg).where(Words.user_id == user_id, Words.word == word).execute()


def delete_word(user_id, word):
    try:
        row = Words.get(Words.user_id == user_id, Words.word == word)
    except DoesNotExist:
        return 0
    return row.delete_instance()


def get_all_words_for_user(user_id):
    return Words.select().where(Words.user_id == user_id)


def get_all_active_users():
    return Users.select().where(Users.chat_id > 0, Users.sleep != 0)


if __name__ == '__main__':
    if not os.path.exists('base.db'):
        db.start()
        Users.create_table()
        Words.create_table()
        Users.create(chat_id=0)
        db.stop()
