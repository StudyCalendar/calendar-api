import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

db = create_engine(
    os.getenv("DB_URL")
    # "postgresql://postgres:160724@127.0.0.1:5432/postgres"
)
base = declarative_base()

Session = sessionmaker(db)
