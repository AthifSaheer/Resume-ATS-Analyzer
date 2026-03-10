from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class CompanyTrack(Base):
    __tablename__ = "company_track"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(255), nullable=False)
    jd = Column(Text, nullable=True)
    resume = Column(Text, nullable=True)          # extracted text from uploaded PDF
    resume_filename = Column(String(255), nullable=True)
    new_resume = Column(Text, nullable=True)      # extracted text from updated PDF
    new_resume_filename = Column(String(255), nullable=True)
    ai_response = Column(Text, nullable=True)     # JSON string of AI response
    status = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

DATABASE_URL = "sqlite:///./company_track.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass