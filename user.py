from db import session, base
from sqlalchemy import String, Boolean, Float, DateTime, Sequence, select
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.sql import func
from pydantic import BaseModel
from nanoid import generate
import datetime
from fastapi import APIRouter
from db import db

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],

)


class User(base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(Sequence('user_id_seq'), primary_key=True)
    public_id: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    nickname: Mapped[str] = mapped_column(String(10))
    login_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())


class UserCreate(BaseModel):
    nickname: str
    login_id: str
    password: str


# base.metadata.create_all(db)


@router.post("/create")
def user_create(user_create: UserCreate):
    db_user = User(public_id=generate('0123456789abcdefghijklmnopqrstuvwxyz', 12),
                   nickname=user_create.nickname,
                   password=user_create.password,
                   login_id=user_create.login_id)
    session.add(db_user)
    session.commit()
    return {"message": "성공"}
