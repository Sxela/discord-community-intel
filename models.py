# models.py
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DB_URL

Base = declarative_base()
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

class WelcomeUser(Base):
    __tablename__ = 'welcome_users'
    user_id = Column(String, primary_key=True)
    username = Column(String)
    joined_at = Column(DateTime)

class Introduction(Base):
    __tablename__ = 'introductions'
    user_id = Column(String, primary_key=True)
    intro_message = Column(Text)
    intro_time = Column(DateTime)

class SocialProfile(Base):
    __tablename__ = 'social_profiles'
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    platform = Column(String)
    url = Column(String)
    followers = Column(Integer)
    source_message = Column(Text)  # NEW: Full message where this URL was extracted

class ParsedLog(Base):
    __tablename__ = 'parsed_log'
    id = Column(Integer, primary_key=True)
    channel = Column(String)
    last_parsed = Column(DateTime)

Base.metadata.create_all(engine)
