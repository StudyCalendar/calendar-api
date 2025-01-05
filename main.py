from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "신광희엉덩이"}
