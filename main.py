from fastapi import FastAPI
from user import router

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "신광희엉덩이"}

app.include_router(router)
