import json
import psycopg2
from psycopg2 import pool
from app.core.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

# db_pool = pool.SimpleConnectionPool(
#     minconn=1, maxconn=10,
#     dbname=DB_NAME, 
#     user=DB_USER,
#     password=DB_PASSWORD, 
#     host=DB_HOST, 
#     port=DB_PORT
# )

# def get_db_connection():
#     return db_pool.getconn()

# def release_db_connection(conn):
#     db_pool.putconn(conn)

# def create_table():
#     query = """
#     CREATE TABLE IF NOT EXISTS all_resume_json (
#         id SERIAL PRIMARY KEY,
#         file_name TEXT UNIQUE NOT NULL,
#         resume_data JSONB NOT NULL
#     );
#     """
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute(query)
#     conn.commit()
#     cur.close()
#     release_db_connection(conn)


# Connect to PostgreSQL
def connect_db():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

# Create table if not exists
def create_table():
    query = """
    CREATE TABLE IF NOT EXISTS all_resume_json (
        id SERIAL PRIMARY KEY,
        file_name TEXT UNIQUE NOT NULL,
        resume_data JSONB NOT NULL
    );
    """
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    cur.close()
    conn.close()

# Check if a file already exists in the database
def file_exists(file_name):
    query = "SELECT 1 FROM all_resume_json WHERE file_name = %s;"
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(query, (file_name,))
    exists = cur.fetchone() is not None
    cur.close()
    conn.close()
    return exists

# Insert JSON data into the table
def insert_json_data(file_name, json_data):
    query = """
    INSERT INTO all_resume_json (file_name, resume_data) 
    VALUES (%s, %s);
    """
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(query, (file_name, json.dumps(json_data)))
    conn.commit()
    cur.close()
    conn.close()

# Fetch all records from the table
def get_all_json_data():
    query = "SELECT file_name, resume_data FROM all_resume_json;"
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(query)
    records = cur.fetchall()
    cur.close()
    conn.close()
    return [{"file_name": record[0], "resume_data": record[1]} for record in records]
