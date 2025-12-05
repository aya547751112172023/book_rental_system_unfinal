from fastapi import FastAPI
from api import register_routes

app = FastAPI()

# Register all the routes from the book_rental folder
register_routes(app=app)


@app.get("/")
def home():
    return {"message": "FastAPI"}
