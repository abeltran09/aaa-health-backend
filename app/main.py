from fastapi import FastAPI
import database
from api.main import api_router

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

app.include_router(api_router)