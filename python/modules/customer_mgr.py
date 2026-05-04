import sys
import os
from mysql.connector import Error 

# 1. Setup system paths to find database_conn.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database_conn import get_connection

def add_customer(name, phone):
    """
    Registers a new customer using:
    - CustomerName: name
    - PhoneNumber: phone
    """
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # 100% matches your existing database column names
            query = "INSERT INTO customers (CustomerName, PhoneNumber) VALUES (%s, %s)"
            cursor.execute(query, (name, str(phone).strip()))
            conn.commit()
            
            new_id = cursor.lastrowid # Critical for the Booking UI to link the ticket
            return new_id, f"✅ Customer '{name}' added successfully."
        except Error as e:
            return None, f"❌ MySQL Error: {e}"
        finally:
            conn.close()
    return None, "❌ Unable to connect to the Database."

def find_customer_by_phone(phone):
    """
    Critical for the Booking UI: Searches by PhoneNumber.
    """
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # 100% matches your existing database column names
            query = "SELECT CustomerID, CustomerName FROM customers WHERE PhoneNumber = %s"
            cursor.execute(query, (str(phone).strip(),))
            result = cursor.fetchone()
            
            if result:
                return result, "Success"
            return None, "No customer found with this phone number."
        except Error as e:
            return None, f"❌ MySQL Error: {e}"
        finally:
            conn.close()
    return None, "❌ Connection Error."

def list_all_customers():
    """
    Retrieves full customer list for Management/Admin dashboard.
    """
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # Fetches all columns including CustomerName and PhoneNumber
            cursor.execute("SELECT * FROM customers ORDER BY CustomerID DESC")
            return cursor.fetchall()
        except Error as e:
            print(f"Error: {e}")
            return []
        finally:
            conn.close()
    return []