from app import create_app, db
from app.models.product import Product

app = create_app()

with app.app_context():
    count = Product.query.count()
    print(f"Total products in DB: {count}")
    
    # Check for a specific item from CSV
    p = Product.query.filter_by(sku='TECH-LAP-001').first()
    if p:
        print(f"Found: {p.name} - {p.category.name}")
