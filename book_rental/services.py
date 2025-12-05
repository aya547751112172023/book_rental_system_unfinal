from mysql.connector.connection import MySQLConnection
from mysql.connector import Error
from fastapi import HTTPException
from . import models

# ==========================================
# BOOK SERVICES (CRUD)
# ==========================================

def get_books(conn: MySQLConnection):
    cursor = conn.cursor(dictionary=True)
    # Fetch only active books
    query = "SELECT * FROM books WHERE is_active = TRUE"
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return results

def get_book_by_id(conn: MySQLConnection, payload: models.Delete_Book):
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM books WHERE id = %s"
    values = (payload.book_id,)
    cursor.execute(query, values)
    result = cursor.fetchone()
    cursor.close()
    return result

def insert_book(conn: MySQLConnection, payload: models.Insert_Book):
    cursor = conn.cursor()
    query = """
    INSERT INTO books (title, author, genre, total_copies, available_copies) 
    VALUES (%s, %s, %s, %s, %s)
    """
    # When creating a book, available_copies equals total_copies initially
    values = (
        payload.title, 
        payload.author, 
        payload.genre, 
        payload.total_copies, 
        payload.total_copies
    )
    cursor.execute(query, values)
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    return new_id

def update_book(conn: MySQLConnection, payload: models.Update_Book):
    cursor = conn.cursor()
    updates = []
    params = []

    # Dynamic query building: only update what is sent
    if payload.total_copies is not None:
        updates.append("total_copies = %s")
        params.append(payload.total_copies)
    
    if payload.is_active is not None:
        updates.append("is_active = %s")
        params.append(payload.is_active)
    
    if not updates:
        return 0

    query = f"UPDATE books SET {', '.join(updates)} WHERE id = %s"
    params.append(payload.book_id)

    cursor.execute(query, tuple(params))
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    return affected

def delete_book(conn: MySQLConnection, payload: models.Delete_Book):
    # Soft Delete: We just mark it as inactive
    cursor = conn.cursor()
    query = "UPDATE books SET is_active = FALSE WHERE id = %s"
    values = (payload.book_id,)
    cursor.execute(query, values)
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    return affected

# ==========================================
# RENTAL SERVICES (TRANSACTIONS)
# ==========================================

def rent_book(conn: MySQLConnection, payload: models.Insert_Rental):
    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Check if book exists and has copies available
        # FOR UPDATE locks the row so no one else can rent the last copy simultaneously
        check_query = "SELECT available_copies FROM books WHERE id = %s FOR UPDATE"
        cursor.execute(check_query, (payload.book_id,))
        book = cursor.fetchone()

        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        if book['available_copies'] < 1:
            raise HTTPException(status_code=400, detail="No copies available")

        # 2. Create the Rental Record
        rent_query = "INSERT INTO rentals (user_id, book_id) VALUES (%s, %s)"
        cursor.execute(rent_query, (payload.user_id, payload.book_id))
        rental_id = cursor.lastrowid

        # 3. Decrease the Book Inventory
        update_stock = "UPDATE books SET available_copies = available_copies - 1 WHERE id = %s"
        cursor.execute(update_stock, (payload.book_id,))

        conn.commit()
        cursor.close()
        return rental_id

    except Error as e:
        conn.rollback()
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Database Transaction Failed")

def return_book(conn: MySQLConnection, payload: models.Delete_Rental):
    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Find the rental record
        find_query = "SELECT book_id, returned_at FROM rentals WHERE id = %s"
        cursor.execute(find_query, (payload.rental_id,))
        rental = cursor.fetchone()

        if not rental:
            raise HTTPException(status_code=404, detail="Rental ID not found")
        
        if rental['returned_at'] is not None:
            raise HTTPException(status_code=400, detail="Book already returned")

        # 2. Mark as Returned
        return_query = "UPDATE rentals SET returned_at = NOW() WHERE id = %s"
        cursor.execute(return_query, (payload.rental_id,))

        # 3. Increase Book Inventory
        update_stock = "UPDATE books SET available_copies = available_copies + 1 WHERE id = %s"
        cursor.execute(update_stock, (rental['book_id'],))

        conn.commit()
        cursor.close()
        return "Book returned successfully"

    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))