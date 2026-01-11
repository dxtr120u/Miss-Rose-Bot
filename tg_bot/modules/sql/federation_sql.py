from sqlalchemy import Column, String
from sqlalchemy.orm import sessionmaker, declarative_base

from tg_bot.modules.sql import BASE, SESSION

Base = declarative_base()

class Federation(BASE):
    __tablename__ = 'federation'
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id

Federation.__table__.create(bind=SESSION.get_bind(), checkfirst=True)

def add_to_fed(chat_id):
    fed = Federation(str(chat_id))
    SESSION.add(fed)
    SESSION.commit()

def rm_from_fed(chat_id):
    fed = SESSION.query(Federation).filter(Federation.chat_id == str(chat_id)).first()
    if fed:
        SESSION.delete(fed)
        SESSION.commit()

def get_all_feds():
    return SESSION.query(Federation).all()
