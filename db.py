import mysql.connector
from mysql.connector import Error 

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="#1234",
            database="expense_tracker"
        )
        if conn.is_connected():
            return conn
        else:
            return None
    except Error as e:
        print("Error while connecting to MySQL:",e)
        return None
    
def execute_query(query, params=None):
    conn = get_connection()
    if not conn :
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        conn.commit()
        return True
    except Error as e:
        print("Database error in execute_query:", e)
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def fetch_all(query, params=None):
    conn = get_connection()
    if not conn :
        return []
    
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        return rows
    except Error as e:
        print("Database error in fetch_all:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def fetch_one(query, params=None):
    conn = get_connection()
    if not conn :
        return None
    
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        row = cursor.fetchone()
        return row
    except Error as e:
        print("Database error in fetch_one:", e)
        return None
    finally:
        cursor.close()
        conn.close() 
