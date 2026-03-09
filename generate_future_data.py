import random
from datetime import datetime, timedelta
import calendar
from app import create_app, db
from app.models.product import Product
from app.models.stock_movement import StockMovement

app = create_app()

def generate_monthly_stress_test_data():
    with app.app_context():
        products = Product.query.all()
        if not products:
            print("No products found to attach data to")
            return
            
        movement_count = 0
        
        # We start from January 2025 up to April 2027 based on "all months including next year April 2027"
        start_year = 2025
        end_year = 2027
        end_month = 4
        
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                if year == end_year and month > end_month:
                    break
                    
                # Number of days in this month
                _, num_days = calendar.monthrange(year, month)
                
                # 50 Adds (IN)
                for _ in range(50):
                    day = random.randint(1, num_days)
                    hour = random.randint(8, 20)
                    minute = random.randint(0, 59)
                    txn_date = datetime(year, month, day, hour, minute)
                    
                    product = random.choice(products)
                    qty = random.randint(10, 50)
                    
                    movement = StockMovement(
                        product_id=product.id,
                        movement_type="IN",
                        quantity=qty,
                        timestamp=txn_date
                    )
                    db.session.add(movement)
                    product.quantity += qty
                    movement_count += 1
                
                # 10 Removes (OUT)
                for _ in range(10):
                    day = random.randint(1, num_days)
                    hour = random.randint(8, 20)
                    minute = random.randint(0, 59)
                    txn_date = datetime(year, month, day, hour, minute)
                    
                    product = random.choice(products)
                    qty = random.randint(1, 10)
                    
                    movement = StockMovement(
                        product_id=product.id,
                        movement_type="OUT",
                        quantity=qty,
                        timestamp=txn_date
                    )
                    db.session.add(movement)
                    product.quantity = max(0, product.quantity - qty)
                    movement_count += 1
                    
        db.session.commit()
        print(f"Successfully generated {movement_count} stock movements up to April 2027.")

if __name__ == "__main__":
    generate_monthly_stress_test_data()
