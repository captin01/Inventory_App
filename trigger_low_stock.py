from datetime import datetime
from app import create_app, db
from app.models.product import Product
from app.models.stock_movement import StockMovement

app = create_app()

def trigger_low_stock():
    with app.app_context():
        # Get the first two products
        products = Product.query.limit(2).all()
        
        for p in products:
            # Set quantity intentionally low
            p.quantity = 4
            
            # Create a recent OUT movement so it appears in the fast-dropping list
            movement = StockMovement(
                product_id=p.id,
                movement_type="OUT",
                quantity=5,
                timestamp=datetime.now()
            )
            db.session.add(movement)
            print(f"Successfully triggered low stock for: {p.name}")
            
        db.session.commit()

if __name__ == "__main__":
    trigger_low_stock()
