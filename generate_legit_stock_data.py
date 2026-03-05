import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models.product import Product
from app.models.stock_movement import StockMovement

app = create_app()

def generate_legit_data():
    with app.app_context():
        products = Product.query.all()
        end_date = datetime.now()
        
        movement_count = 0
        
        # We will loop through all products and add a realistic flow of IN and OUT movements
        # over the past 90 days.
        count = 0
        for product in products:
            movements_to_add = []
            
            # Create IN movements (Restocks)
            num_in = random.randint(2, 6)
            for _ in range(num_in):
                days_ago = random.randint(1, 90)
                # Add random hours/minutes for realism
                h = random.randint(8, 20)
                m = random.randint(0, 59)
                txn_date = end_date - timedelta(days=days_ago, hours=h, minutes=m)
                
                qty = random.randint(20, 100)
                movements_to_add.append({
                    "product_id": product.id,
                    "movement_type": "IN",
                    "quantity": qty,
                    "timestamp": txn_date
                })
            
            # Create OUT movements (Sales or usages)
            num_out = random.randint(15, 40)
            for _ in range(num_out):
                days_ago = random.randint(1, 90)
                h = random.randint(8, 20)
                m = random.randint(0, 59)
                txn_date = end_date - timedelta(days=days_ago, hours=h, minutes=m)
                
                qty = random.randint(1, 5)
                movements_to_add.append({
                    "product_id": product.id,
                    "movement_type": "OUT",
                    "quantity": qty,
                    "timestamp": txn_date
                })
                
            # Sort movements by timestamp
            movements_to_add.sort(key=lambda x: x["timestamp"])
            
            # Apply movements and update product quantity
            net_change = sum(m["quantity"] if m["movement_type"] == "IN" else -m["quantity"] for m in movements_to_add)
            
            # Ensure quantity doesn't become totally unrealistic (e.g., negative).
            # The UI logic gracefully handles negative stock but it's better to stay realistic.
            product.quantity = max(0, product.quantity + net_change)
            
            for m in movements_to_add:
                movement = StockMovement(
                    product_id=m["product_id"],
                    movement_type=m["movement_type"],
                    quantity=m["quantity"],
                    timestamp=m["timestamp"]
                )
                db.session.add(movement)
                movement_count += 1
            
            count += 1

        db.session.commit()
        print(f"Successfully generated {movement_count} legit stock movements across {count} products.")

if __name__ == "__main__":
    print("Generating legit stock data...")
    generate_legit_data()
    print("Done!")
