from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

from tg_bot.modules.sql import BASE, SESSION

Base = declarative_base()

class Reputation(BASE):
    __tablename__ = 'reputation'
    id = Column(Integer, primary_key=True)
    chat_id = Column(String(14), nullable=False)
    user_id = Column(Integer, nullable=False)
    reputation = Column(Integer, default=0)

    def __init__(self, chat_id, user_id):
        self.chat_id = chat_id
        self.user_id = user_id
        self.reputation = 0

Reputation.__table__.create(bind=SESSION.get_bind(), checkfirst=True)

def get_rep(chat_id, user_id):
    rep = SESSION.query(Reputation).filter(Reputation.chat_id == str(chat_id), Reputation.user_id == user_id).first()
    if rep:
        return rep.reputation
    return 0

def add_rep(chat_id, user_id, amount):
    rep = SESSION.query(Reputation).filter(Reputation.chat_id == str(chat_id), Reputation.user_id == user_id).first()
    if rep:
        rep.reputation += amount
    else:
        rep = Reputation(str(chat_id), user_id)
        rep.reputation = amount
        SESSION.add(rep)
    
    SESSION.commit()
    return rep.reputation

def rm_rep(chat_id, user_id, amount):
    rep = SESSION.query(Reputation).filter(Reputation.chat_id == str(chat_id), Reputation.user_id == user_id).first()
    if rep:
        rep.reputation -= amount
        SESSION.commit()
        return rep.reputation
    return 0

def rm_user(chat_id, user_id):
    rep = SESSION.query(Reputation).filter(Reputation.chat_id == str(chat_id), Reputation.user_id == user_id).first()
    if rep:
        SESSION.delete(rep)
        SESSION.commit()

def get_chat_leaderboard(chat_id):
    return SESSION.query(Reputation).filter(Reputation.chat_id == str(chat_id)).order_by(Reputation.reputation.desc()).limit(10).all()

