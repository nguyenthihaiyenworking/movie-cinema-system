import sys
import os
import pandas as pd
import streamlit as st
from mysql.connector import Error

# 1. Setup system paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database_conn import get_connection

# --- 1. DATA RETRIEVAL FUNCTIONS ---

def get_movie_revenue_report(movie_id):
    """Uses SQL Function to get revenue for a specific movie."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # Dùng MovieTitle theo schema của Yen
            cursor.execute("SELECT MovieTitle FROM movies WHERE MovieID = %s", (movie_id,))
            movie = cursor.fetchone()
            
            if not movie:
                return None, f"❌ Movie ID {movie_id} not found."

            cursor.execute("SELECT GetMovieRevenue(%s) AS total_revenue", (movie_id,))
            result = cursor.fetchone()
            
            revenue = result['total_revenue'] if result['total_revenue'] is not None else 0
            return {"title": movie['MovieTitle'], "revenue": float(revenue)}, "Success"
        except Error as e:
            return None, f"❌ Error: {e}"
        finally:
            conn.close()
    return None, "❌ Connection Error."

def get_top_customers(limit=5):
    """Fetches top customers by ticket count."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT c.CustomerName, COUNT(t.TicketID) as TotalTickets
                FROM customers c
                JOIN tickets t ON c.CustomerID = t.CustomerID
                GROUP BY c.CustomerID, c.CustomerName
                ORDER BY TotalTickets DESC
                LIMIT %s
            """
            cursor.execute(query, (limit,))
            return cursor.fetchall()
        finally:
            conn.close()
    return []

def get_revenue_by_tier():
    """Lấy dữ liệu doanh thu theo hạng ghế."""
    conn = get_connection()
    if not conn: return None
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT st.TypeName AS Seat_Tier, COUNT(t.TicketID) as Sold, SUM(t.TotalPrice) as Revenue
            FROM seat_types st
            JOIN seats s ON st.TypeID = s.TypeID
            JOIN tickets t ON s.SeatID = t.SeatID
            GROUP BY st.TypeName
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Error as e:
        print(f"Error: {e}")
        return None
    finally:
        conn.close()

def get_revenue_by_room_type():
    """Lấy dữ liệu doanh thu theo loại phòng."""
    conn = get_connection()
    if not conn: return None
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                r.RoomName AS Room_Type,
                COUNT(t.TicketID) AS Sold,
                SUM(t.TotalPrice) AS Revenue
            FROM cinemarooms r
            JOIN screenings scr ON r.RoomID = scr.RoomID
            JOIN tickets t ON scr.ScreeningID = t.ScreeningID
            GROUP BY r.RoomName
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Error as e:
        print(f"Error: {e}")
        return None
    finally:
        conn.close()

def get_all_movies_revenue_summary():
    """Call SQL function GetMovieRevenue for each movie"""
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(dictionary=True)
        # Sửa Title -> MovieTitle để khớp với hàm get_movie_revenue_report của Yen
        cursor.execute("SELECT MovieID, MovieTitle FROM movies")
        movies = cursor.fetchall()
        
        summary = []
        for m in movies:
            query = "SELECT GetMovieRevenue(%s) AS revenue" 
            cursor.execute(query, (m['MovieID'],))
            result = cursor.fetchone()
            
            summary.append({
                "title": m['MovieTitle'],
                "revenue": float(result['revenue']) if result['revenue'] else 0.0
            })
        return summary
    except Exception as e:
        print(f"Error calling SQL function: {e}")
        return []
    finally:
        conn.close()

# --- BỔ SUNG HÀM THIẾU Ở ĐÂY ---
def get_occupancy_report():
    """Calculates occupancy rate using ShowDate from Yen's schema."""
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(dictionary=True)
        # 1. Sử dụng ShowDate thay cho StartTime
        # 2. Sử dụng LEFT JOIN để đảm bảo hiện đủ 510 suất chiếu
        query = """
            SELECT 
                m.MovieTitle,
                s.ShowDate, 
                r.RoomName,
                s.ScreeningID,
                (SELECT COUNT(*) FROM tickets t WHERE t.ScreeningID = s.ScreeningID) AS SoldSeats,
                (SELECT COUNT(*) FROM seats se WHERE se.RoomID = r.RoomID) AS TotalSeats
            FROM screenings s
            LEFT JOIN movies m ON s.MovieID = m.MovieID
            LEFT JOIN cinemarooms r ON s.RoomID = r.RoomID
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        if not results:
            return []
            
        report = []
        for res in results:
            total = res['TotalSeats'] if res['TotalSeats'] else 0
            sold = res['SoldSeats'] if res['SoldSeats'] else 0
            occupancy = sold / total if total > 0 else 0
            
            report.append({
                "Movie": res['MovieTitle'] if res['MovieTitle'] else "N/A",
                "Time": str(res['ShowDate']), # Chuyển ShowDate sang string để Streamlit hiển thị
                "Room": res['RoomName'] if res['RoomName'] else "N/A",
                "Occupancy_Rate": occupancy
            })
        return report
    except Exception as e:
        st.error(f"Database Error: {e}")
        return []
    finally:
        conn.close()

if __name__ == "__main__":
    print("--- 📊 Cinema Analytics Module ---")
    top_fans = get_top_customers(3)
    for fan in top_fans:
        print(f"Customer: {fan['CustomerName']} | Tickets: {fan['TotalTickets']}")