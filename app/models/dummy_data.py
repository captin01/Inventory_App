import mysql.connector
import random
from datetime import datetime, timedelta

# -----------------------------
# 1. CONNECT TO MYSQL DATABASE
# -----------------------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    port=3306,
    database="inventory_db"   # <-- change this to your actual DB name
)

cursor = conn.cursor()

print("\nConnected to MySQL successfully!\n")

# ---------------------------------------
# 2. INSERT DUMMY DATA INTO categories
# ---------------------------------------
categories = [
    ("Electronics", "Electronic items such as phones and accessories"),
    ("Clothing", "Apparel including shirts, pants, and jackets"),
    ("Groceries", "Everyday food and household groceries"),
    ("Furniture", "Tables, chairs, and home furniture"),
    ("Stationery", "Office and school stationery items"),
]

cursor.execute("DELETE FROM stock_movements")
cursor.execute("DELETE FROM products")
cursor.execute("DELETE FROM categories")

category_insert_query = """
INSERT INTO categories (name, description)
VALUES (%s, %s)
"""

cursor.executemany(category_insert_query, categories)
conn.commit()

print("Inserted categories successfully!")

# -------------------------------------------------
# 3. Fetch category IDs for foreign key assignment
# -------------------------------------------------
cursor.execute("SELECT id, name FROM categories")
category_rows = cursor.fetchall()

category_map = {name: cid for cid, name in category_rows}

# ---------------------------------------
# 4. INSERT 20+ DUMMY PRODUCTS
# ---------------------------------------
products = [
    ("iPhone Charger", 15.99, 120, category_map["Electronics"]),
    ("Wireless Mouse", 12.49, 85, category_map["Electronics"]),
    ("Bluetooth Speaker", 29.99, 40, category_map["Electronics"]),
    ("Men's T-Shirt", 9.99, 200, category_map["Clothing"]),
    ("Women's Jacket", 49.99, 35, category_map["Clothing"]),
    ("Jeans Pants", 25.99, 60, category_map["Clothing"]),
    ("Rice (5kg)", 7.99, 150, category_map["Groceries"]),
    ("Cooking Oil (1L)", 3.49, 90, category_map["Groceries"]),
    ("Cereal Box", 5.29, 110, category_map["Groceries"]),
    ("Office Chair", 79.99, 20, category_map["Furniture"]),
    ("Study Desk", 119.00, 10, category_map["Furniture"]),
    ("Bookshelf", 59.99, 15, category_map["Furniture"]),
    ("A4 Notebook", 1.49, 300, category_map["Stationery"]),
    ("Ballpoint Pen Pack", 2.99, 400, category_map["Stationery"]),
    ("Highlighter Set", 4.99, 180, category_map["Stationery"]),
    
    # Extra products to ensure over 20
    ("USB Cable", 5.99, 140, category_map["Electronics"]),
    ("LED Desk Lamp", 14.99, 55, category_map["Electronics"]),
    ("Hoodie Sweatshirt", 19.99, 120, category_map["Clothing"]),
    ("Milk 1L", 1.99, 200, category_map["Groceries"]),
    ("Pencil Pack", 1.29, 250, category_map["Stationery"]),
]

cursor.execute("DELETE FROM products")

# Generate SKU for each product (required field, must be unique)
products_with_sku = []
sku_set = set()  # Track used SKUs to ensure uniqueness
for idx, (name, price, quantity, category_id) in enumerate(products, 1):
    # Generate a simple SKU from product name
    base_sku = "SKU-" + name.upper().replace(" ", "-").replace("'", "").replace("(", "").replace(")", "").replace("/", "-")[:15]
    sku = base_sku
    counter = 1
    # Ensure uniqueness by appending number if needed
    while sku in sku_set:
        sku = f"{base_sku}-{counter}"
        counter += 1
    sku_set.add(sku)
    products_with_sku.append((name, sku, price, quantity, category_id))

product_insert_query = """
INSERT INTO products (name, sku, price, quantity, category_id)
VALUES (%s, %s, %s, %s, %s)
"""

cursor.executemany(product_insert_query, products_with_sku)
conn.commit()

print("Inserted 20+ products successfully!")

# ---------------------------------------
# 5. INSERT DUMMY STOCK MOVEMENTS
# ---------------------------------------
cursor.execute("SELECT id, quantity FROM products")
product_rows = cursor.fetchall()

stock_movement_insert = """
INSERT INTO stock_movements (product_id, movement_type, quantity, timestamp)
VALUES (%s, %s, %s, %s)
"""

movements = []

for pid, qty in product_rows:
    # Create random inflow/outflow
    # Use 'IN' and 'OUT' to match the StockMovement model Enum
    movement_type = random.choice(["IN", "OUT"])
    movement_qty = random.randint(1, 15)

    timestamp = datetime.now() - timedelta(days=random.randint(0, 30))

    movements.append((
        pid,
        movement_type,
        movement_qty,
        timestamp
    ))

cursor.executemany(stock_movement_insert, movements)
conn.commit()

print("Inserted stock movements successfully!\n")

# -----------------------------
# CLOSE CONNECTION
# -----------------------------
cursor.close()
conn.close()

print("All dummy data inserted successfully!")
