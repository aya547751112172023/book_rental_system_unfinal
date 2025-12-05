from fastapi import FastAPI

# import controllers here
from book_rental.controller import router as book_rental_router

#


def register_routes(app: FastAPI):
    # register controllers here
    app.include_router(prefix="/api/v1", tags=["book_rental"], router=book_rental_router)


