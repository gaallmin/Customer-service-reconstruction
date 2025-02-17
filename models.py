from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class UserFeedback(Base):
    __tablename__ = 'ankh_db'
    id = Column(Integer, primary_key=True, autoincrement=True)
    reservation_opinion = Column(Text)
    health_issues = Column(Text)
    ankh_help = Column(Text)

DATABASE_URL = "mysql+pymysql://admin:ankh-survey-db.c78y4ugsgy3q.us-east-1.rds.amazonaws.com:3306/ankh"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
