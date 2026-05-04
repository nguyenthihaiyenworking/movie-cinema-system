import sys
import os
from mysql.connector import Error

# Ensure the database connection file is recognized
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database_conn import get_connection

def check_login(username, password):
    """Validates login credentials and records the login event."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # 1. Verify credentials
            query = """
                SELECT AccountID, Username, Role 
                FROM accounts 
                WHERE Username = %s AND Password = %s
            """
            cursor.execute(query, (username, password))
            user_data = cursor.fetchone()
            
            if user_data:
                # 2. Log successful login
                log_query = """
                    INSERT INTO logs (AccountID, ActionType, TableName, LogDetails)
                    VALUES (%s, 'LOGIN', 'accounts', %s)
                """
                cursor.execute(log_query, (user_data['AccountID'], f"User {username} logged in."))
                conn.commit()
                return user_data, "Login successful!"
            else:
                return None, "Invalid username or password."
                
        except Error as e:
            return None, f"System Error: {str(e)}"
        finally:
            conn.close()
    return None, "Unable to connect to the database."

# --- ADMINISTRATIVE FUNCTIONS ---

def get_all_logs(limit=100):
    """Admin tool to monitor system activity."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # Ensure your logs table has LogTimestamp or change to your actual column name
            query = "SELECT * FROM logs ORDER BY LogTimestamp DESC LIMIT %s"
            cursor.execute(query, (limit,))
            return cursor.fetchall()
        except Error as e:
            print(f"Log query error: {e}")
            return []
        finally:
            conn.close()
    return []

def list_accounts():
    """Retrieves a list of all accounts."""
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT AccountID, Username, FullName, Role FROM accounts")
        return cursor.fetchall()
    finally:
        conn.close()

def add_account(username, password, fullname, role):
    """Creates a new user account."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "INSERT INTO accounts (Username, Password, FullName, Role) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (username, password, fullname, role))
        conn.commit()
        return True, "Account created successfully!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_account(acc_id, fullname, role, password=None):
    """Updates account information (optional password update included)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if password:
            query = "UPDATE accounts SET FullName=%s, Role=%s, Password=%s WHERE AccountID=%s"
            cursor.execute(query, (fullname, role, password, acc_id))
        else:
            query = "UPDATE accounts SET FullName=%s, Role=%s WHERE AccountID=%s"
            cursor.execute(query, (fullname, role, acc_id))
        conn.commit()
        return True, "Update successful!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def delete_account(acc_id):
    """Removes an account from the database."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM accounts WHERE AccountID = %s", (acc_id,))
        conn.commit()
        return True, "Account deleted successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()