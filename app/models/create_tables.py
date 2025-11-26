import mysql.connector
from mysql.connector import Error

def create_tables():
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",      # update if needed
            port=3306
        )

        if conn.is_connected():
            print("✓ Connected to MySQL")

            cursor = conn.cursor()

            # Select the database
            cursor.execute("USE Inventory;")
            print("✓ Using database 'Inventory'")

            # ---------- CREATE TABLES ----------
            table_queries = [

                """
                CREATE TABLE IF NOT EXISTS categories (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT
                );
                """,

                """
                CREATE TABLE IF NOT EXISTS products (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(150) NOT NULL,
                    category_id INT,
                    price DECIMAL(10,2) NOT NULL,
                    stock INT DEFAULT 0,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                );
                """,

                """
                CREATE TABLE IF NOT EXISTS stock_movements (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    product_id INT NOT NULL,
                    quantity INT NOT NULL,
                    movement_type ENUM('IN','OUT') NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                );
                """
            ]

            # Execute each SQL statement
            for query in table_queries:
                cursor.execute(query)

            conn.commit()
            print("✓ Tables created successfully.")

    except Error as e:
        print("❌ Error:", e)

    finally:
        # Close connection
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("✓ MySQL connection closed.")

# Run script
if __name__ == "__main__":
    create_tables()
