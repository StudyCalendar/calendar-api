from sqlalchemy import create_engine, Column, String, Boolean, Integer, Float, DateTime, Sequence, select
from sqlalchemy.orm import sessionmaker, declarative_base, mapped_column, Mapped
from sqlalchemy.sql import func
from nanoid import generate
import datetime


db = create_engine(
    "postgresql://postgres:160724@127.0.0.1:5432/postgres"
)
base = declarative_base()

Session = sessionmaker(db)
session = Session()


# class User(base):
#     __tablename__ = 'user'
#     id: Mapped[int] = mapped_column(Sequence('user_id_seq'), primary_key=True)
#     public_id: Mapped[str] = mapped_column(String(12), unique=True, index=True)
#     nickname: Mapped[str] = mapped_column(String(10))
#     login_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
#     password: Mapped[str] = mapped_column(String(255))
#     created_at: Mapped[datetime.datetime] = mapped_column(
#         DateTime(timezone=True), server_default=func.now())


# base.metadata.create_all(db)

# kimyurim = User(
#     public_id=generate('0123456789abcdefghijklmnopqrstuvwxyz', 12),
#     login_id="qkfkaajvls",
#     nickname="김유림",
#     password="djasdkjlf"
# )

# session.query(User).delete()
# session.add_all([kimyurim])

# session.commit()


# user_find = select(User).where(User.login_id == "qkfkaajvls")
# for user in session.scalars(user_find):
#     print(user.nickname)

# kimyurim.nickname = "김유림1"

# session.commit()

# user_find = select(User).where(User.login_id == "qkfkaajvls")
# for user in session.scalars(user_find):
#     print(user.nickname)

# # session.delete(kimyurim)

# session.commit()

# user_find = select(User).where(User.login_id == "qkfkaajvls")
# for user in session.scalars(user_find):
#     print(user.nickname)
