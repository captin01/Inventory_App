from app import db
from datetime import datetime

class StockMovement(db.Model):
    __tablename__ = "stock_movements"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    product = db.relationship("Product", backref="stock_movements", lazy=True)
    quantity = db.Column(db.Integer, nullable=False)
    movement_type = db.Column(db.Enum('IN', 'OUT'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<StockMovement {self.movement_type} {self.quantity}>"
