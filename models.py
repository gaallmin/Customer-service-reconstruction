import os
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

DB_HOST = os.environ.get('RDS_HOSTNAME')
DB_PORT = os.environ.get('RDS_PORT')
DB_NAME = os.environ.get('RDS_DB_NAME')
DB_USER = os.environ.get('RDS_USERNAME')
DB_PASS = os.environ.get('RDS_PASSWORD')

class UserFeedback(Base):
    __tablename__ = 'ankh_db'
    id = Column(Integer, primary_key=True, autoincrement=True)
    reservation_opinion = Column(Text)
    health_issues = Column(Text)
    ankh_help = Column(Text)

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
