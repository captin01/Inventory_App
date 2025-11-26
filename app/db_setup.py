import mysql.connector
from mysql.connector import Error

def test_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",   # add your password if you have one
            port=3306
        )

        if conn.is_connected():
            print("✓ Connected to MySQL")
            print("User:", conn.user)
            print("Server version:", conn.get_server_info())

        return conn

    except Error as err:
        print("❌ Connection error:", err)


def create_database():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            port=3306
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS inventory;")
        print("✓ Database 'inventory' is ready.")
        cursor.close()
        conn.close()
    except Error as err:
        print("❌ Error creating database:", err)

if __name__ == "__main__":
    test_connection()
    create_database()
