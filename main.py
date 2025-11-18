from fastapi import FastAPI
from api import register_routes

app = FastAPI()

register_routes(app=app)


@app.get("/")
def home():
    return {"message": "FastAPI"}
