from peewee import *
from playhouse.sqliteq import SqliteQueueDatabase

db = SqliteQueueDatabase('base.db')


class BaseModel(Model):
    class Meta:
        database = db


class Users(BaseModel):
    chat_id = IntegerField(unique=True)
    sleep = IntegerField(default=0)
    send_at = TimestampField(default=0)
    answer_at = TimestampField(default=0)


class Words(BaseModel):
    user_id = ForeignKeyField(Users, on_delete='CASCADE')
    word = CharField()
    translate = CharField()
    transcript = CharField(null=True)
    weight = IntegerField(default=100)

    class Meta:
        indexes = (
            (('word', 'user_id'), True),
        )
