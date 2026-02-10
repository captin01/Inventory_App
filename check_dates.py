from app import create_app, db
from app.models.stock_movement import StockMovement
from sqlalchemy import func

app = create_app()

with app.app_context():
    # Check distribution of dates
    print("Stock Movement Date Distribution:")
    movements = db.session.query(
        func.date(StockMovement.timestamp), func.count(StockMovement.id)
    ).group_by(func.date(StockMovement.timestamp)).order_by(func.date(StockMovement.timestamp)).all()
    
    # Print first few and last few days covering the range
    if movements:
        print(f"Earliest date: {movements[0][0]}")
        print(f"Latest date: {movements[-1][0]}")
        print(f"Total active days: {len(movements)}")
    else:
        print("No movements found.")
