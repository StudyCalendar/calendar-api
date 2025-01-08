from sqlalchemy import create_engine, Column, String, Boolean, Integer, Float, DateTime, Sequence
from sqlalchemy.orm import sessionmaker, declarative_base
from nanoid import generate


db = create_engine(
    "postgresql://postgres:160724@127.0.0.1:5432/postgres"
)
base = declarative_base()

Session = sessionmaker(db)
session = Session()


class User(base):
    __tablename__ = 'user'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    public_id = Column(String(12), unique=True, index=True)
    login_id = Column(String(100), unique=True, index=True)
    password = Column(String(255))


base.metadata.create_all(db)

kimyurim = User(
    public_id=generate('0123456789abcdefghijklmnopqrstuvwxyz', 12),
    login_id="qkfkajvls",
    password="djasdkjlf"
)
session.add_all([kimyurim])
session.commit()
