import os
from fastapi import FastAPI
from dotenv import load_dotenv

import user
import verification


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "신광희엉덩이"}

app.include_router(user.router)
app.include_router(verification.router)
