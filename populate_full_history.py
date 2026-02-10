import csv
import os
import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models.product import Product
from app.models.category import Category
from app.models.stock_movement import StockMovement

app = create_app()

def import_csv(filename):
    if not os.path.exists(filename):
        print(f"File {filename} not found.")
        return

    print(f"Importing products from {filename}...")
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Get or Create Category
                category_name = row['category_name'].strip()
                category = Category.query.filter_by(name=category_name).first()
                if not category:
                    category = Category(name=category_name, description=f"Category for {category_name}")
                    db.session.add(category)
                    db.session.commit()
                
                # Create Update Product
                sku = row['sku'].strip()
                product = Product.query.filter_by(sku=sku).first()
                if not product:
                    product = Product(
                        name=row['name'].strip(),
                        sku=sku,
                        price=float(row['price']),
                        quantity=int(row['quantity']),
                        category_id=category.id
                    )
                    # Set created_at to a random date in the past (3-12 months ago)
                    days_ago = random.randint(90, 365)
                    product.created_at = datetime.utcnow() - timedelta(days=days_ago)
                    
                    db.session.add(product)
                else:
                    # Update existing
                    product.name = row['name'].strip()
                    product.price = float(row['price'])
                    product.quantity = int(row['quantity'])
                    product.category_id = category.id
                    # Don't update created_at if it already exists, unless it's very recent (implying we just made it)
            except Exception as e:
                print(f"Error processing row {row}: {e}")
                db.session.rollback()
        
        db.session.commit()
        print(f"Finished importing products from {filename}.")

def generate_stock_history():
    print("Generating historical stock movements...")
    products = Product.query.all()
    
    # Time window: last 6 months
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=180)
    
    movement_count = 0
    
    for product in products:
        # Check if product already has movements to avoid over-populating on re-runs
        if len(product.stock_movements) > 5: 
            # Logic: If it already has history, maybe skip or add just a few recent ones. 
            # For this task, let's assume we can add more if needed, but let's limit it.
            continue
            
        # Determine how many movements to create
        num_movements = random.randint(15, 50)
        
        for _ in range(num_movements):
            # Random date between start_date and now
            days_offset = random.randint(0, 180)
            txn_date = end_date - timedelta(days=days_offset)
            
            # Determine type: mostly sales (OUT), some restocks (IN)
            if random.random() < 0.7:
                m_type = 'OUT'
                qty = random.randint(1, 5)
            else:
                m_type = 'IN'
                qty = random.randint(10, 50)
            
            movement = StockMovement(
                product_id=product.id,
                movement_type=m_type,
                quantity=qty,
                timestamp=txn_date
            )
            db.session.add(movement)
            movement_count += 1
            
    db.session.commit()
    print(f"Successfully created {movement_count} stock movements across {len(products)} products.")

if __name__ == "__main__":
    with app.app_context():
        # 1. Import/Update Products
        import_csv('tech_store_data.csv')
        import_csv('grocery_store_data.csv')
        
        # 2. Generate History
        generate_stock_history()
