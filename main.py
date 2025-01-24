import os
from fastapi import FastAPI, HTTPException, Request
from dotenv import load_dotenv
from db import Session
from sqlalchemy import String, Boolean, Float, DateTime, Sequence, select, and_, update
import time

from fastapi.responses import JSONResponse
from user import User
import user
import verification
import jwt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "hello world"}

app.include_router(user.router)
app.include_router(verification.router)

#


def verify_token(access_token: str):
    with Session() as session:
        try:
            # 디코드 후 public_id 뽑아서 user 디비 조회 후 return
            access_payload = jwt.decode(access_token, os.getenv(
                "ACCESS_SECRET_KEY"), algorithms=['HS256'])

            public_id: str = access_payload.get("public_id")

            stmt = select(User).where(User.public_id == public_id)

            return session.execute(stmt).scalar_one_or_none()

        except Exception as e:
            # return False
            print(e)
        raise HTTPException(status_code=401, detail="Invalid ID token")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    if request.url.path in ["/docs", "/openapi.json", "/auth/register", "/auth/login", "/verifications/email", "/verifications/confirm"]:
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    print('auth_header:', auth_header)
    if not auth_header or not auth_header.startswith('Bearer'):
        return JSONResponse(status_code=403, content={'status': 403})

    token = auth_header.split(' ')[1]
    print(token)

    user_info = verify_token(token)
    print('user_info:', user_info)

    if user_info is None:
        return JSONResponse(status_code=403, content={'status': 403})

    request.state.user = user_info

    return await call_next(request)
