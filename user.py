from db import Session, base
from sqlalchemy import String, Boolean, Float, DateTime, Sequence, select
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.sql import func
from pydantic import BaseModel
from nanoid import generate
from datetime import timedelta
from fastapi import APIRouter, HTTPException
from db import db
import jwt
import os
import bcrypt
import datetime
from enum import Enum

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


class Userlogin(BaseModel):
    login_id: str
    password: str


base.metadata.create_all(db)


@router.post("/create")
def user_create(user_create: UserCreate):
    with Session() as session:
        try:
            # 중복 확인 쿼리 작성
            stmt = select(User).where(User.login_id == user_create.login_id)
            existing_user = session.execute(stmt).scalar_one_or_none()

            if existing_user:
                raise HTTPException(status_code=400, detail="이미 존재하는 아이디입니다.")

            # 새로운 사용자 생성
            new_user = User(
                public_id=generate('0123456789abcdefghijklmnopqrstuvwxyz', 12),
                nickname=user_create.nickname,
                login_id=user_create.login_id,
                password=bcrypt.hashpw(
                    user_create.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            )
            session.add(new_user)
            session.commit()

            return {"status": "success", "message": "회원가입이 완료되었습니다."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"오류 발생: {e}")


@router.post("/login")
def user_login(user_login: Userlogin):
    with Session() as session:
        try:
            # 사용자 확인
            stmt = select(User).where(User.login_id == user_login.login_id)
            user = session.execute(stmt).scalar_one_or_none()

            if not user:
                raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다.")

            # 비밀번호 확인
            if not bcrypt.checkpw(
                user_login.password.encode(
                    'utf-8'), user.password.encode('utf-8')
            ):
                raise HTTPException(status_code=401, detail="비밀번호가 잘못되었습니다.")

            # 액세스 토큰발급
            access_payload = {
                "public_id": user.public_id,
                "exp": datetime.datetime.now() + timedelta(minutes=30)
            }

            access_token = jwt.encode(
                access_payload, os.getenv("ACCESS_SECRET_KEY"), algorithm='HS256')

            # 리프레시 토큰발급
            refresh_payload = {
                "public_id": user.public_id,
                "exp": datetime.datetime.now() + timedelta(days=7)
            }

            refresh_token = jwt.encode(
                refresh_payload, os.getenv("REFRESH_SECRET_KEY"), algorithm='HS256')

            return {"message": "성공", "access_token": access_token, "refresh_token": refresh_token}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"오류 발생: {e}")
