from fastapi import APIRouter, Depends
from database import get_db_connection
from mysql.connector.connection import MySQLConnection

from .models import (
    Insert_Book, 
    Delete_Book, 
    Update_Book, 
    Insert_Rental, 
    Delete_Rental
)

from .services import (
    get_books,
    get_book_by_id,
    insert_book,
    update_book,
    delete_book,
    rent_book,
    return_book
)

router = APIRouter(prefix="/library")

# ==========================================
# BOOK ROUTES
# ==========================================

@router.get("/books")
def api_get_books(conn: MySQLConnection = Depends(get_db_connection)):
    try:
        data = get_books(conn=conn)
        return {"data": data}
    except Exception as e:
        return {"message": "Error fetching books", "error": str(e)}

@router.post("/books")
def api_insert_book(
    payload: Insert_Book, conn: MySQLConnection = Depends(get_db_connection)
):
    try:
        new_id = insert_book(conn=conn, payload=payload)
        return {"message": f"Book added with ID: {new_id}"}
    except Exception as e:
        return {"message": "Error adding book", "error": str(e)}

@router.post("/books/detail")
def api_get_book(
    payload: Delete_Book, conn: MySQLConnection = Depends(get_db_connection)
):
    try:
        data = get_book_by_id(conn=conn, payload=payload)
        return {"data": data}
    except Exception as e:
        return {"message": "Error fetching book", "error": str(e)}

@router.patch("/books")
def api_update_book(
    payload: Update_Book, conn: MySQLConnection = Depends(get_db_connection)
):
    try:
        affected = update_book(conn=conn, payload=payload)
        return {"message": f"{affected} book(s) updated"}
    except Exception as e:
        return {"message": "Error updating book", "error": str(e)}

@router.delete("/books")
def api_delete_book(
    payload: Delete_Book, conn: MySQLConnection = Depends(get_db_connection)
):
    try:
        affected = delete_book(conn=conn, payload=payload)
        return {"message": f"{affected} book(s) marked inactive"}
    except Exception as e:
        return {"message": "Error deleting book", "error": str(e)}

# ==========================================
# RENTAL ROUTES
# ==========================================

@router.post("/rent")
def api_rent_book(
    payload: Insert_Rental, conn: MySQLConnection = Depends(get_db_connection)
):
    """Rents a book to a user and decreases stock"""
    try:
        rental_id = rent_book(conn=conn, payload=payload)
        return {"message": f"Rental successful. Rental ID: {rental_id}"}
    except Exception as e:
        return {"message": "Error processing rental", "error": str(e)}

@router.post("/return")
def api_return_book(
    payload: Delete_Rental, conn: MySQLConnection = Depends(get_db_connection)
):
    """Returns a book and increases stock"""
    try:
        msg = return_book(conn=conn, payload=payload)
        return {"message": msg}
    except Exception as e:
        return {"message": "Error processing return", "error": str(e)}