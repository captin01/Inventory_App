from flask import render_template, session, redirect, url_for
from datetime import datetime, timedelta
from sqlalchemy import func, case

from . import bp
from app.models.product import Product
from app.models.category import Category
from app.models.stock_movement import StockMovement
from app.routes.auth import login_required
from app import db


@bp.route("/")
def landing():
    """Public landing page (always shown, even if authenticated)."""
    return render_template("landing.html")


@bp.route("/dashboard")
@login_required
def home():
    # Calculate metrics
    product_count = Product.query.count()
    category_count = Category.query.count()
    stock_movements_count = StockMovement.query.count()
    
    # Calculate total stock value
    stock_value = db.session.query(
        func.sum(Product.price * Product.quantity)
    ).scalar() or 0
    
    # Count low stock items (quantity < 10)
    low_stock = Product.query.filter(Product.quantity < 10).count()
    
    # Get recent movements (last 10)
    recent_movements = db.session.query(StockMovement).join(Product).order_by(
        StockMovement.timestamp.desc()
    ).limit(10).all()
    
    # Prepare recent movements data
    movements_data = []
    for move in recent_movements:
        movements_data.append({
            "product": move.product.name if move.product else "Unknown",
            "type": "inbound" if move.movement_type == "IN" else "outbound",
            "quantity": move.quantity,
            "timestamp": move.timestamp.strftime("%Y-%m-%d %H:%M") if move.timestamp else "N/A"
        })
    
    # Get stock movements for last 7 days for chart
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_movements = db.session.query(
        func.date(StockMovement.timestamp).label('date'),
        func.sum(case((StockMovement.movement_type == 'IN', StockMovement.quantity), else_=0)).label('inbound'),
        func.sum(case((StockMovement.movement_type == 'OUT', StockMovement.quantity), else_=0)).label('outbound')
    ).filter(
        StockMovement.timestamp >= seven_days_ago
    ).group_by(
        func.date(StockMovement.timestamp)
    ).order_by(
        func.date(StockMovement.timestamp)
    ).all()
    
    # Prepare chart data
    chart_labels = []
    inbound_data = []
    outbound_data = []
    
    # If no data, provide default empty arrays
    if not daily_movements:
        # Generate last 7 days labels
        for i in range(6, -1, -1):
            date = datetime.utcnow() - timedelta(days=i)
            chart_labels.append(date.strftime("%m/%d"))
            inbound_data.append(0)
            outbound_data.append(0)
    else:
        for day in daily_movements:
            # Handle possible string return from func.date() (e.g. SQLite returns 'YYYY-MM-DD')
            date_val = day.date
            if isinstance(date_val, str):
                try:
                    # Parse YYYY-MM-DD string
                    date_obj = datetime.strptime(date_val, "%Y-%m-%d")
                    chart_labels.append(date_obj.strftime("%m/%d"))
                except ValueError:
                    # Fallback if format is unexpected
                    chart_labels.append(date_val)
            elif date_val:
                # It's a date/datetime object
                chart_labels.append(date_val.strftime("%m/%d"))
            else:
                chart_labels.append("")

            inbound_data.append(int(day.inbound or 0))
            outbound_data.append(int(day.outbound or 0))
    
    # Get category distribution for pie chart
    category_data = db.session.query(
        Category.name,
        func.count(Product.id).label('count')
    ).join(Product, Category.id == Product.category_id, isouter=True).group_by(
        Category.id, Category.name
    ).all()
    
    category_labels = [cat.name for cat in category_data] if category_data else []
    category_counts = [int(cat.count or 0) for cat in category_data] if category_data else []
    
    return render_template(
        "pages/dashboard.html",
        metrics={
            "product_count": product_count,
            "category_count": category_count,
            "stock_movements_count": stock_movements_count,
            "stock_value": round(stock_value, 2),
            "low_stock": low_stock,
            "recent_movements": movements_data,
            "chart_labels": chart_labels,
            "inbound_data": inbound_data,
            "outbound_data": outbound_data,
            "category_labels": category_labels,
            "category_counts": category_counts,
        },
    )

