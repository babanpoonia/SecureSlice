from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = 'postgresql://postgres:postgres@localhost/secure_slice_db'

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class PacketLog(Base):
    __tablename__ = 'packet_logs'
    id = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP)
    source_ip = Column(String)
    dest_ip = Column(String)
    protocol = Column(String)
    length = Column(Integer)
