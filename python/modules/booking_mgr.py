import sys
import os
from datetime import datetime, timedelta
from mysql.connector import Error

# 1. Setup path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database_conn import get_connection

# Terminal Color Class for Debugging
class C:
    RESET    = "\033[0m"
    BOLD     = "\033[1m"
    BCYAN    = "\033[96m"
    BGREEN   = "\033[92m"
    BRED     = "\033[91m"
    BYELLOW  = "\033[93m"
    DIM      = "\033[2m"

# --- CORE FUNCTIONS ---

def book_ticket(customer_id, screening_id, seat_id, price,account_id):
    """Executes booking via Procedure and ensures DB consistency."""
    conn = get_connection()
    if not conn: return None
    try:
        cursor = conn.cursor()
        # Call the procedure (Make sure your SQL Proc updates 'seats' status to 'Booked')
        cursor.callproc('BookTicket', (customer_id, screening_id, seat_id, price, account_id))
        conn.commit()
        return True
    except Error as e:
        print(f"  {C.BRED}❌ Booking error: {e.msg}{C.RESET}")
        return False
    finally:
        conn.close()

def list_bookings():
    """FIXED: JOINs all tables correctly including your preserved column names."""
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT t.TicketID, c.CustomerName, m.MovieTitle, s.SeatNumber, t.BookingDate, t.TotalPrice
            FROM tickets t
            JOIN customers c ON t.CustomerID = c.CustomerID
            JOIN screenings scr ON t.ScreeningID = scr.ScreeningID
            JOIN movies m ON scr.MovieID = m.MovieID
            JOIN seats s ON t.SeatID = s.SeatID
            ORDER BY t.BookingDate DESC
            LIMIT 50;
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Error as e:
        print(f"  {C.BRED}Error loading bookings: {e}{C.RESET}")
        return []
    finally:
        conn.close()

def get_seat_info(seat_id):
    """Retrieves seat number and pricing information based on seat type."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT s.SeatNumber, st.BasePrice, st.TypeName 
            FROM seats s
            JOIN seat_types st ON s.TypeID = st.TypeID
            WHERE s.SeatID = %s
        """
        cursor.execute(query, (seat_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def delete_ticket(ticket_id):
    """Deletes a ticket and resets the seat status to 'Available'."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # 1. Get SeatID before deleting ticket to reset status
        cursor.execute("SELECT SeatID FROM tickets WHERE TicketID = %s", (ticket_id,))
        res = cursor.fetchone()
        if res:
            seat_id = res[0]
            # 2. Delete ticket
            cursor.execute("DELETE FROM tickets WHERE TicketID = %s", (ticket_id,))
            # 3. Reset seat
            cursor.execute("UPDATE seats SET Status = 'Available', LockedUntil = NULL WHERE SeatID = %s", (seat_id,))
            conn.commit()
            return True
    except Error as e:
        print(f"Error deleting ticket: {e}")
        return False
    finally:
        conn.close()
        
def get_seats_by_room(room_id):
    """Retrieves all seats in a specific room along with their category information."""
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                s.SeatID, 
                s.SeatNumber, 
                s.RowChar, 
                s.Status, 
                s.LockedUntil,
                st.TypeName, 
                st.BasePrice
            FROM seats s
            JOIN seat_types st ON s.TypeID = st.TypeID
            WHERE s.RoomID = %s
            ORDER BY s.RowChar, s.SeatNumber
        """
        cursor.execute(query, (room_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error retrieving seat list: {e}")
        return []
    finally:
        conn.close()

def book_seat_with_lock(seat_id, account_id):
    """
    Locks a seat for 15 mins. 
    Note: In a professional system, this should also check ScreeningID.
    """
    conn = get_connection()
    if not conn: return False, "Connection error."
    try:
        cursor = conn.cursor(dictionary=True)
        
        # 1. Check current seat status
        cursor.execute("SELECT Status, LockedUntil FROM seats WHERE SeatID = %s", (seat_id,))
        seat = cursor.fetchone()
        
        if not seat: return False, "Seat not found."

        current_time = datetime.now()
        if seat['Status'] == 'Booked':
            return False, "This seat is already sold."
        if seat['Status'] == 'Locked' and seat['LockedUntil'] and seat['LockedUntil'] > current_time:
            return False, "Seat is held by another staff member."

        # 2. Lock the seat
        lock_until = current_time + timedelta(minutes=15)
        cursor.execute("UPDATE seats SET Status = 'Locked', LockedUntil = %s WHERE SeatID = %s", 
                       (lock_until, seat_id))
        
        # 3. Log (Using your ActionType 'UPDATE')
        log_query = "INSERT INTO logs (AccountID, ActionType, TableName, LogDetails) VALUES (%s, 'UPDATE', 'seats', %s)"
        cursor.execute(log_query, (account_id, f"Locked SeatID {seat_id} until {lock_until.strftime('%H:%M:%S')}"))
        
        conn.commit()
        return True, f"Locked until {lock_until.strftime('%H:%M:%S')}"
    except Exception as e:
        if conn: conn.rollback()
        return False, f"System error: {str(e)}"
    finally:
        conn.close()

# --- CUSTOMER HELPERS (Preserving Your Names) ---

def get_customer_by_phone(phone):
    """Consistent with customer_mgr.py"""
    conn = get_connection()
    if not conn: return None
    try:
        cursor = conn.cursor(dictionary=True)
        # Matches CustomerName and PhoneNumber
        cursor.execute("SELECT CustomerID, CustomerName FROM customers WHERE PhoneNumber = %s", (str(phone).strip(),))
        return cursor.fetchone()
    finally:
        conn.close()

def add_new_customer(name, phone):
    """
    Adds a new customer to the database and returns the generated CustomerID.
    Uses the exact column names 'CustomerName' and 'PhoneNumber' as requested.
    """
    conn = get_connection()
    if not conn: 
        return None
        
    try:
        cursor = conn.cursor()
        # Ensure phone number is treated as a string and whitespace is removed
        query = "INSERT INTO customers (CustomerName, PhoneNumber) VALUES (%s, %s)"
        cursor.execute(query, (name, str(phone).strip()))
        conn.commit()
        
        # Return the auto-generated ID to immediately facilitate the booking process
        return cursor.lastrowid  
    except Error as e:
        print(f"Error while adding customer: {e}")
        return None
    finally:
        conn.close()