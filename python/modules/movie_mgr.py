import sys
import os
from mysql.connector import Error

# 1. Setup system paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from database_conn import get_connection

# --- GENRE MANAGEMENT ---

def add_genre(genre_name):
    """Inserts a new genre into the genres table."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO genres (GenreName) VALUES (%s)", (genre_name,))
            conn.commit()
            return True, f"Genre added: {genre_name}"
        except Error as e:
            return False, f"Error adding genre: {e}"
        finally:
            conn.close()

def list_genres():
    """Retrieves all genres sorted by name."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM genres ORDER BY GenreName")
            return cursor.fetchall()
        finally:
            conn.close()
    return []

# --- MOVIE MANAGEMENT (Updated for Many-to-Many) ---

def add_movie(title, genre_ids, duration, release_date, rating):
    """
    Inserts a movie and links it to multiple genres.
    genre_ids: list of IDs (e.g., [1, 3]) representing the selected genres.
    """
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # 1. Insert into movies table (Junction table handles genres now)
            query_movie = """INSERT INTO movies (MovieTitle, DurationMinutes, ReleaseDate, Rating) 
                             VALUES (%s, %s, %s, %s)"""
            cursor.execute(query_movie, (title, duration, release_date, rating))
            new_movie_id = cursor.lastrowid

            # 2. Insert relationships into movie_genres junction table
            query_mg = "INSERT INTO movie_genres (MovieID, GenreID) VALUES (%s, %s)"
            for g_id in genre_ids:
                cursor.execute(query_mg, (new_movie_id, g_id))
            
            conn.commit()
            return True, "Movie and its Genres added successfully!"
        except Error as e:
            conn.rollback()
            return False, f"Error adding movie: {e}"
        finally:
            conn.close()

def list_movies():
    """Retrieves the movie list with concatenated genres for a unified view."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # GROUP_CONCAT aggregates multiple genres into a single string
            query = """
                SELECT m.MovieID, m.MovieTitle, 
                       GROUP_CONCAT(g.GenreName SEPARATOR ', ') as Genres, 
                       DurationMinutes, m.ReleaseDate, m.Rating 
                FROM movies m
                LEFT JOIN movie_genres mg ON m.MovieID = mg.MovieID
                LEFT JOIN genres g ON mg.GenreID = g.GenreID
                GROUP BY m.MovieID
            """
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error retrieving movie list: {e}")
            return []
        finally:
            conn.close()
    return []

# --- SCREENING MANAGEMENT (Updated for ShowDate DATETIME) ---

def get_all_screenings():
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(dictionary=True)
        # Lấy trực tiếp từ screenings, không JOIN để tránh mất dòng do lệch ID
        query = "SELECT ScreeningID, MovieID, RoomID, ShowDate FROM screenings ORDER BY ShowDate DESC"
        cursor.execute(query)
        return cursor.fetchall()
    except Error as e:
        st.error(f"Error: {e}")
        return []
    finally:
        conn.close()

def add_screening(movie_id, room_id, show_date):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO screenings (MovieID, RoomID, ShowDate) VALUES (%s, %s, %s)",
                       (movie_id, room_id, show_date))
        conn.commit()
        return True, "Added screening!"
    except Error as e:
        return False, str(e)
    finally:
        conn.close()

def update_screening(screening_id, movie_id, room_id, show_date):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "UPDATE screenings SET MovieID=%s, RoomID=%s, ShowDate=%s WHERE ScreeningID=%s"
        cursor.execute(query, (movie_id, room_id, show_date, screening_id))
        conn.commit()
        return True, "Updated screening!"
    except Error as e:
        return False, str(e)
    finally:
        conn.close()

def delete_screening(screening_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM screenings WHERE ScreeningID = %s", (screening_id,))
        conn.commit()
        return True, "Deleted screening!"
    except Error as e:
        return False, "Cannot delete: Tickets already sold for this screening."
    finally:
        conn.close()



def delete_movie(movie_id):
    """Removes a movie record from the database."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM movies WHERE MovieID = %s", (movie_id,))
            conn.commit()
            return True, "Movie deleted successfully."
        except Error as e:
            return False, f"System Error during deletion: {e}"
        finally:
            conn.close()
    return False, "Database connection failed."

def update_movie(movie_id, title, duration, release_date, rating):
    """Cập nhật thông tin phim đã tồn tại."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                UPDATE movies 
                SET MovieTitle = %s, Duration = %s, ReleaseDate = %s, Rating = %s 
                WHERE MovieID = %s
            """
            cursor.execute(query, (title, duration, release_date, rating, movie_id))
            conn.commit()
            return True, "Movie updated successfully!"
        except Error as e:
            return False, f"Error: {e}"
        finally:
            conn.close()
    return False, "Connection Error."

def update_genre(genre_id, new_name):
    """Cập nhật tên thể loại phim."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE genres SET GenreName = %s WHERE GenreID = %s", (new_name, genre_id))
            conn.commit()
            return True, "Genre updated successfully!"
        except Error as e:
            return False, f"Error: {e}"
        finally:
            conn.close()
    return False, "Connection Error."

def delete_genre(genre_id):
    """Xóa thể loại phim (Lưu ý: Sẽ lỗi nếu có phim đang thuộc thể loại này)."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM genres WHERE GenreID = %s", (genre_id,))
            conn.commit()
            return True, "Genre deleted successfully!"
        except Error as e:
            # Lỗi thường gặp: Cannot delete or update a parent row (Foreign key constraint)
            return False, f"Cannot delete: This genre is being used by movies."
        finally:
            conn.close()
    return False, "Connection Error."

def get_all_screenings():
    """Lấy danh sách suất chiếu kèm tên phim và tên phòng."""
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                s.ScreeningID, 
                m.MovieTitle, 
                r.RoomName, 
                s.ShowDate, 
                s.MovieID, 
                s.RoomID, 
                m.DurationMinutes
            FROM screenings s
            LEFT JOIN movies m ON s.MovieID = m.MovieID
            LEFT JOIN cinemarooms r ON s.RoomID = r.RoomID
            ORDER BY s.ShowDate DESC
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        st.error(f"Lỗi SQL: {e}")
        return []
    finally:
        conn.close()

def check_overlap(room_id, new_show_time, new_movie_duration, current_screening_id=None):
    """Kiểm tra trùng lịch dựa trên thời lượng thực tế của phim."""
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor(dictionary=True)
        # Đồng bộ tên cột DurationMinutes trong câu lệnh logic
        query = """
            SELECT s.ScreeningID 
            FROM screenings s
            JOIN movies m ON s.MovieID = m.MovieID
            WHERE s.RoomID = %s
            AND s.ScreeningID != %s
            AND (
                (%s BETWEEN s.ShowDate AND DATE_ADD(s.ShowDate, INTERVAL m.DurationMinutes MINUTE))
                OR 
                (DATE_ADD(%s, INTERVAL %s MINUTE) BETWEEN s.ShowDate AND DATE_ADD(s.ShowDate, INTERVAL m.DurationMinutes MINUTE))
            )
        """
        exclude_id = current_screening_id if current_screening_id else -1
        cursor.execute(query, (room_id, exclude_id, new_show_time, new_show_time, new_movie_duration))
        return cursor.fetchone() is not None
    finally:
        conn.close()

def has_future_screenings(movie_id):
    """
    Checks if a movie has any scheduled screenings from current time onwards.
    Prevents deleting a movie that still has shows to run.
    """
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        # Use ShowDate and NOW() to find upcoming screenings
        query = "SELECT COUNT(*) FROM screenings WHERE MovieID = %s AND ShowDate >= NOW()"
        cursor.execute(query, (movie_id,))
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        print(f"Error checking future screenings: {e}")
        return False
    finally:
        conn.close()

def list_rooms():
    """Retrieves a list of all cinema rooms from the database."""
    conn = get_connection()
    if not conn: 
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        # Double check if your table name is 'cinemarooms' or 'rooms'
        query = "SELECT RoomID, RoomName FROM cinemarooms" 
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching rooms: {e}")
        return []
    finally:
        conn.close()

def add_room(room_name, capacity):
    """Adds a new cinema room to the cinemarooms table."""
    conn = get_connection()
    if not conn: return False, "Database connection error"
    try:
        cursor = conn.cursor()
        query = "INSERT INTO cinemarooms (RoomName, Capacity) VALUES (%s, %s)"
        cursor.execute(query, (room_name, capacity))
        conn.commit()
        return True, f"Room '{room_name}' added successfully!"
    except Error as e:
        return False, f"SQL Error: {e}"
    finally:
        conn.close()

def list_rooms():
    """Retrieves the complete list of cinema rooms."""
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cinemarooms")
        return cursor.fetchall()
    finally:
        conn.close()

def list_seat_types():
    """Retrieves a list of seat types (VIP, Standard, etc.)."""
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM seat_types")
        return cursor.fetchall()
    finally:
        conn.close()

def add_seat_type(type_name, base_price):
    """Adds a new seat type and its corresponding price."""
    conn = get_connection()
    if not conn: return False, "Connection error"
    try:
        cursor = conn.cursor()
        query = "INSERT INTO seat_types (TypeName, BasePrice) VALUES (%s, %s)"
        cursor.execute(query, (type_name, base_price))
        conn.commit()
        return True, f"Seat type '{type_name}' has been added."
    except Error as e:
        return False, f"Error: {e}"
    finally:
        conn.close()

def update_seat_type(type_id, new_price):
    """Updates the price for an existing seat type."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "UPDATE seat_types SET BasePrice = %s WHERE TypeID = %s"
        cursor.execute(query, (new_price, type_id))
        conn.commit()
        return True, "Price updated successfully!"
    except Error as e:
        return False, str(e)
    finally:
        conn.close()

def delete_seat_type(type_id):
    """Deletes a seat type (Note: Will fail if seats are currently assigned to this type)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM seat_types WHERE TypeID = %s", (type_id,))
        conn.commit()
        return True, "Seat type deleted."
    except Error as e:
        return False, f"Cannot delete: {e}"
    finally:
        conn.close()

def copy_room_layout(source_room_id, target_room_id):
    """Copies the entire seat structure from one room to another."""
    conn = get_connection()
    if not conn: return False, "Connection error"
    try:
        cursor = conn.cursor()
        # Fetch seats from the template room
        cursor.execute("SELECT TypeID, RowChar, SeatNumber FROM seats WHERE RoomID = %s", (source_room_id,))
        source_seats = cursor.fetchall()
        
        if not source_seats:
            return False, "Template room contains no seat data."

        # Insert into the target room
        query = """
            INSERT INTO seats (RoomID, TypeID, RowChar, SeatNumber, Status) 
            VALUES (%s, %s, %s, %s, 'Available')
        """
        # Prepare data for bulk insertion
        val_list = [(target_room_id, s[0], s[1], s[2]) for s in source_seats]
        cursor.executemany(query, val_list)
        
        conn.commit()
        return True, f"Successfully copied {len(source_seats)} seats to room {target_room_id}."
    except Error as e:
        return False, f"Copy error: {e}"
    finally:
        conn.close()