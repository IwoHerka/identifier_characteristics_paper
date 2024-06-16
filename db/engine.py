from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base


USERNAME = "admin"
PASSWORD = "password"
HOST = "localhost"
PORT = "5432"
DATABASE = "namebench"


def get_engine():
    DATABASE_URL = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
    return create_engine(DATABASE_URL)


engine = get_engine()

Base = declarative_base()
