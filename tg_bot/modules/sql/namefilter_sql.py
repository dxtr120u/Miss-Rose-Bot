from sqlalchemy import Column, String
from sqlalchemy.orm import sessionmaker, declarative_base

from tg_bot.modules.sql import BASE, SESSION

Base = declarative_base()

class NameFilterSettings(BASE):
    __tablename__ = 'namefilter_settings'
    chat_id = Column(String(14), primary_key=True)
    message = Column(String, default="User {first_name} has a blacklisted name. Should I take action?")

    def __init__(self, chat_id):
        self.chat_id = chat_id

NameFilterSettings.__table__.create(bind=SESSION.get_bind(), checkfirst=True)

def get_message(chat_id):
    setting = SESSION.query(NameFilterSettings).filter(NameFilterSettings.chat_id == str(chat_id)).first()
    if setting:
        return setting.message
    return "User {first_name} has a blacklisted name. Should I take action?"

def set_message(chat_id, message):
    setting = SESSION.query(NameFilterSettings).filter(NameFilterSettings.chat_id == str(chat_id)).first()
    if setting:
        setting.message = message
    else:
        setting = NameFilterSettings(str(chat_id))
        setting.message = message
        SESSION.add(setting)
    
    SESSION.commit()
