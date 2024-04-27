from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base


USERNAME = 'admin'
PASSWORD = 'password'
HOST = 'localhost'
PORT = '5432'
DATABASE = 'namebench'

DATABASE_URL = f'postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'
engine = create_engine(DATABASE_URL)

Base = declarative_base()

