from fastapi import FastAPI
import database

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}