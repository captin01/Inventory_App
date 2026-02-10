import csv
import os
from app import create_app, db
from app.models.product import Product
from app.models.category import Category

app = create_app()

def import_csv(filename):
    if not os.path.exists(filename):
        print(f"File {filename} not found.")
        return

    print(f"Importing from {filename}...")
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
                    db.session.commit() # Commit to get ID
                    # print(f"Created Category: {category_name}")
                
                # Create Product
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
                    db.session.add(product)
                    # print(f"Added Product: {row['name']}")
                else:
                    # Update existing
                    product.name = row['name'].strip()
                    product.price = float(row['price'])
                    product.quantity = int(row['quantity'])
                    product.category_id = category.id
                    # print(f"Updated Product: {row['name']}")
            except Exception as e:
                print(f"Error processing row {row}: {e}")
                db.session.rollback()
        
        db.session.commit()
        print(f"Finished importing {filename}.")

if __name__ == "__main__":
    with app.app_context():
        import_csv('tech_store_data.csv')
        import_csv('grocery_store_data.csv')
