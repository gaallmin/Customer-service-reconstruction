from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class UserFeedback(Base):
    __tablename__ = 'user_feedback'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50))
    reservation_opinion = Column(Text)
    health_issues = Column(Text)
    ankh_help = Column(Text)

# MySQL connection string example:
DATABASE_URL = "mysql+pymysql://ankh:ankh03013@localhost:3306/ankh_app_db"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
