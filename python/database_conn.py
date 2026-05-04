import mysql.connector
from mysql.connector import Error

# Centralized configuration for easier updates
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '@0338048344',
    'database': 'cinemadb',
    'auth_plugin': 'mysql_native_password'
}

def get_connection():
    """ 
    Creates and returns a connection to the 'cinemadb' database.
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

def test_connection():
    """ 
    Tests the connection by fetching a sample list of movies.
    """
    conn = get_connection()
    if conn:
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            
            # UPDATED QUERY: Join through the movie_genres junction table
            query = """
                SELECT m.MovieID, m.MovieTitle, g.GenreName
                FROM movies m
                JOIN movie_genres mg ON m.MovieID = mg.MovieID
                JOIN genres g ON mg.GenreID = g.GenreID
                LIMIT 5;
            """

            cursor.execute(query)
            results = cursor.fetchall()
            
            print("--- Connection Successful! Sample Data: ---")
            for row in results:
                print(f"- {row['MovieTitle']} [{row['GenreName']}]")
                
        except Error as e:
            print(f"❌ Query error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

if __name__ == "__main__":
    test_connection()