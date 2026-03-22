import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_connection():
    """
    Establishes a database connection to PostgreSQL.
    
    Uses credentials from environment variables:
    - DB_HOST: Database host 
    - DB_NAME: Database name 
    - DB_USER: Database user 
    - DB_PASSWORD: Database password 
    - DB_PORT: Database port 
    Returns:
        psycopg2.connection: Database connection object
        
    Raises:
        psycopg2.Error: If connection fails
    """
    try:
        # Check for required environment variables
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        
        if not db_user or not db_password:
            raise ValueError(
                "   Missing database credentials in .env file!\n"
                "   Please set DB_USER and DB_PASSWORD environment variables."

            )
        
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "cricbuzz_livestats"),
            user=db_user,
            password=db_password,
            port=os.getenv("DB_PORT", "5432")
        )
        return conn
    except psycopg2.Error as e:
        print(f"Database Connection Error: {e}")
        raise


def execute_query(query, params=None, fetch=False):
    """
    Executes a SQL query with proper error handling.
    
    Args:
        query (str): SQL query to execute
        params (tuple, optional): Parameters for parameterized queries
        fetch (bool): If True, returns query results; if False, executes INSERT/UPDATE/DELETE
        
    Returns:
        list: Query results if fetch=True, None otherwise
        
    Raises:
        psycopg2.Error: If query execution fails
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params)

        if fetch:
            result = cursor.fetchall()
            return result if result else []

        conn.commit()
        affected_rows = cursor.rowcount
        return f"✅ Success! Rows affected: {affected_rows}"

    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"❌ Query Execution Error: {e}")
        raise

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def execute_query_single(query, params=None):
    """
    Executes a query and returns a single row result.
    
    Args:
        query (str): SQL query
        params (tuple, optional): Query parameters
        
    Returns:
        dict: Single row result
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params)
        return cursor.fetchone()
        
    except psycopg2.Error as e:
        print(f"❌ Query Error: {e}")
        raise
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def check_connection():
    """
    Checks if database connection is working.
    
    Returns:
        tuple: (bool: connection status, str: message)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return True, "✅ Database connection successful!"
    except Exception as e:
        return False, f"❌ Database connection failed: {e}"
