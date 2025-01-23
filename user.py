from db import Session, base
from sqlalchemy import String, Boolean, Float, DateTime, Sequence, select, and_, update
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
from verification import Verifications, VerificationType

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],

)

# 기본 데이터베이스 테이블 생성


class User(base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(Sequence('user_id_seq'), primary_key=True)
    public_id: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    nickname: Mapped[str] = mapped_column(String(10))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())

# 회원가입 배이스 모델


class UserCreate(BaseModel):
    nickname: str
    email: str
    password: str
    code_token: str

# 로그인 베이스모델


class Userlogin(BaseModel):
    email: str
    password: str


# 디비 생성
base.metadata.create_all(db)

# 회원가입 api


@router.post("/create")
def user_create(user_create: UserCreate):
    with Session() as session:
        try:
            # 중복 확인 쿼리 작성
            stmt = select(User).where(User.email == user_create.email)
            existing_user = session.execute(stmt).scalar_one_or_none()

            if existing_user:
                raise HTTPException(status_code=400, detail="이미 존재하는 아이디입니다.")

            code_payload = jwt.decode(user_create.code_token, os.getenv(
                "CONFIRM_SECRET_KEY"), algorithms=['HS256'])

            public_id: str = code_payload.get("public_id")

            # 인증 완료 이메일 확인
            confirm = select(Verifications).where(and_
                                                  (
                                                      Verifications.public_id == public_id,
                                                      Verifications.type == VerificationType.register,
                                                      Verifications.used == False,
                                                      Verifications.confirm == True))

            existing_confirm = session.execute(confirm).scalar_one_or_none()

            if not existing_confirm:
                raise HTTPException(status_code=400, detail="인증이 안된 아이디입니다.")

            existing_confirm.used = True

            # 새로운 사용자 생성
            new_user = User(
                public_id=generate('0123456789abcdefghijklmnopqrstuvwxyz', 12),
                nickname=user_create.nickname,
                email=user_create.email,
                password=bcrypt.hashpw(
                    user_create.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            )

            session.add(new_user)
            session.commit()

            return {"message": "success", "message": "회원가입이 완료되었습니다."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"오류 발생: {e}")

# 로그인 api


@router.post("/login")
def user_login(user_login: Userlogin):
    with Session() as session:
        try:
            # 사용자 확인
            stmt = select(User).where(User.email == user_login.email)
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

            return {"message": "success", "data": {"access_token": access_token, "refresh_token": refresh_token}}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"오류 발생: {e}")
