import mysql.connector
from mysql.connector import Error
from app import create_app, db

# Import all models so SQLAlchemy can register them
from app.models.category import Category
from app.models.product import Product
from app.models.stock_movement import StockMovement


def create_database_if_not_exists():
    """Create the database if it doesn't exist."""
    conn = None
    try:
        # Connect to MySQL server (without specifying database)
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            port=3306
        )
        
        if conn.is_connected():
            cursor = conn.cursor()
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS inventory_db;")
            print("✓ Database 'inventory_db' is ready.")
            cursor.close()
            return True
    except Error as err:
        print(f"❌ Error creating database: {err}")
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    try:
        # First ensure database exists
        print("=" * 50)
        print("Setting up database...")
        print("=" * 50)
        if not create_database_if_not_exists():
            print("❌ Failed to create database. Exiting.")
            exit(1)
        
        # Now create the Flask app and tables
        print("\n" + "=" * 50)
        print("Initializing Flask app...")
        print("=" * 50)
        app = create_app()
        
        with app.app_context():
            print("\n" + "=" * 50)
            print("Creating tables...")
            print("=" * 50)
            db.create_all()
            print("✓ All ORM tables created successfully!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
