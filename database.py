from sqlalchemy import create_engine, Column, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class OptionData(Base):
    __tablename__ = 'option_data'
    
    id = Column(String, primary_key=True)
    instrument_name = Column(String)
    price = Column(Float)
    volatility = Column(Float)
    delta = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db():
    db_name = os.getenv('DB_NAME', 'deribit_data.db')
    engine = create_engine(f'sqlite:///{db_name}')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)

def get_last_records(session, limit=100):
    return session.query(OptionData).order_by(OptionData.timestamp.desc()).limit(limit).all()