from flask import render_template, session, redirect, url_for, request
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
    
    month_filter = request.args.get('month', '0')
    try:
        month_filter = int(month_filter)
    except ValueError:
        month_filter = 0
    
    chart_labels = []
    inbound_data = []
    outbound_data = []
    today = datetime.utcnow()
    year = today.year
    seven_days_ago = today - timedelta(days=7)
    
    if 1 <= month_filter <= 12:
        # Get movements for the selected month in the current year
        start_date = datetime(year, month_filter, 1)
        if month_filter == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month_filter + 1, 1)
            
        days_in_month = (end_date - timedelta(days=1)).day
        
        daily_movements = db.session.query(
            func.date(StockMovement.timestamp).label('date'),
            func.sum(case((StockMovement.movement_type == 'IN', StockMovement.quantity), else_=0)).label('inbound'),
            func.sum(case((StockMovement.movement_type == 'OUT', StockMovement.quantity), else_=0)).label('outbound')
        ).filter(
            StockMovement.timestamp >= start_date,
            StockMovement.timestamp < end_date
        ).group_by(
            func.date(StockMovement.timestamp)
        ).order_by(
            func.date(StockMovement.timestamp)
        ).all()
        
        movement_lookup = {}
        for day in daily_movements:
            date_val = day.date
            if isinstance(date_val, str):
                try:
                    date_obj = datetime.strptime(date_val, "%Y-%m-%d")
                    label = date_obj.strftime("%m/%d")
                except ValueError:
                    label = date_val
            elif date_val:
                label = date_val.strftime("%m/%d")
            else:
                continue
            movement_lookup[label] = (int(day.inbound or 0), int(day.outbound or 0))

        # Generate all days for that month
        for d in range(1, days_in_month + 1):
            label = datetime(year, month_filter, d).strftime("%m/%d")
            chart_labels.append(label)
            inbound, outbound = movement_lookup.get(label, (0, 0))
            inbound_data.append(inbound)
            outbound_data.append(outbound)
            
    else:
        # Default: Get stock movements for last 7 days
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
        
        movement_lookup = {}
        for day in daily_movements:
            date_val = day.date
            if isinstance(date_val, str):
                try:
                    date_obj = datetime.strptime(date_val, "%Y-%m-%d")
                    label = date_obj.strftime("%m/%d")
                except ValueError:
                    label = date_val
            elif date_val:
                label = date_val.strftime("%m/%d")
            else:
                continue
            movement_lookup[label] = (int(day.inbound or 0), int(day.outbound or 0))

        # Generate all 7 days, newest last
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            label = date.strftime("%m/%d")
            chart_labels.append(label)
            inbound, outbound = movement_lookup.get(label, (0, 0))
            inbound_data.append(inbound)
            outbound_data.append(outbound)

    
    # Get category distribution for pie chart
    category_data = db.session.query(
        Category.name,
        func.count(Product.id).label('count')
    ).join(Product, Category.id == Product.category_id, isouter=True).group_by(
        Category.id, Category.name
    ).all()
    
    category_labels = [cat.name for cat in category_data] if category_data else []
    category_counts = [int(cat.count or 0) for cat in category_data] if category_data else []
    
    # Get recent low stock due to outbound movements
    recent_low_stock = db.session.query(Product).join(StockMovement).filter(
        StockMovement.movement_type == 'OUT',
        StockMovement.timestamp >= seven_days_ago,
        Product.quantity < 10
    ).group_by(Product.id).limit(5).all()
    
    recent_low_stock_data = [
        {"name": p.name, "quantity": p.quantity} for p in recent_low_stock
    ]
    
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
            "recent_low_stock": recent_low_stock_data,
        },
    )

