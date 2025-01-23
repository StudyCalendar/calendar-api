import os
import jwt
import datetime
import ssl
import smtplib
from enum import Enum
from db import db
from pydantic import BaseModel
from datetime import timedelta
from sqlalchemy.sql import func
from nanoid import generate
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, DateTime, Sequence, Enum as SqlEnum, func, select, and_
from db import Session, base


router = APIRouter(
    prefix="/verifications",
    tags=["Verifications"],

)

# 회원가입, 비밀번호 리셋 타입


class VerificationType(Enum):
    register = "register"
    resetPassword = "resetPassword"

# 인증 기본 데이터베이스 테이블생성


class Verifications(base):
    __tablename__ = 'verification'
    type: Mapped[str] = mapped_column(SqlEnum(VerificationType), index=True)
    target: Mapped[str] = mapped_column(String(100), index=True)
    id: Mapped[int] = mapped_column(
        Sequence('verification_id_seq'), primary_key=True)
    public_id: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    used: Mapped[bool] = mapped_column(default=False)
    confirm: Mapped[bool] = mapped_column(default=False)
    code: Mapped[str] = mapped_column(String(6))

# 이메일 인증 베이스모델


class VerificationEmail(BaseModel):
    type: VerificationType
    email: str

# 이메일 인증확인 베이스모델


class Confirm(BaseModel):
    email_token: str
    code: str


# 디비 생성
base.metadata.create_all(db)

# 이메일 인증발송 api


@router.post("/email")
def register(request: VerificationEmail):
    with Session() as session:
        try:
            # 퍼블릭아이디, 코드 랜덤 생성, 타입지정, 이메일입력
            new_regiser = Verifications(
                public_id=generate('0123456789abcdefghijklmnopqrstuvwxyz', 12),
                code=generate('0123456789', 6),
                type=request.type,
                target=request.email,
            )
            session.add(new_regiser)
            session.commit()

            # 이메일 데이터
            SMTP_SSL_PORT = os.getenv("SENDER_SSL_PORT")
            SMTP_SERVER = os.getenv("SENDER_SERVER")

            sender_email = os.getenv("SENDER_EMAIL")
            sender_password = os.getenv("SENDER_PASSWORD")
            context = ssl.create_default_context()
            receiver_email = request.email

            # 이메일 코드
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_SSL_PORT, context=context) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, new_regiser.code)

            # 이메일 토큰 발급
                email_payload = {
                    "public_id": new_regiser.public_id,
                    "exp": datetime.datetime.now() + timedelta(minutes=5)}

                email_token = jwt.encode(
                    email_payload, os.getenv("EMAIL_SECRET_KEY"), algorithm='HS256')

                return {"message": "success.", "data": {"email_token": email_token}}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"오류 발생: {e}")

# 이메일 인증번호 확인 api


@router.post("/confirm")
def confirm(request: Confirm):
    with Session() as session:
        try:
            # email토큰 디코드
            email_payload = jwt.decode(request.email_token, os.getenv(
                "EMAIL_SECRET_KEY"), algorithms=['HS256'])

            public_id: str = email_payload.get("public_id")

            # email코드로 퍼블릭아이디 찾기
            stmt = select(Verifications).where(
                and_(
                    Verifications.public_id == public_id,
                    Verifications.used == False
                )
            )
            confirm_public_id = session.execute(stmt).scalar_one_or_none()

            # 퍼블릭아이디 확인
            if not confirm_public_id:
                raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다.")

            # 코드확인
            if confirm_public_id.code != request.code:
                raise HTTPException(status_code=401, detail="코드가 일치하지 않습니다.")

            # confirm 트루로 변경
            confirm_public_id.confirm = True

            session.commit()

            # 코드 토큰 발급
            code_payload = {
                "public_id": confirm_public_id.public_id,
                "exp": datetime.datetime.now() + timedelta(minutes=30)}

            code_token = jwt.encode(
                code_payload, os.getenv("CONFIRM_SECRET_KEY"), algorithm='HS256'
            )

            return {"message": "success", "data": {"code_token": code_token}}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"오류 발생: {e}")
