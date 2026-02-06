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
            chart_labels.append(day.date.strftime("%m/%d") if day.date else "")
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
    
    # Get stock value trend for last 7 days
    stock_value_trend_labels = []
    stock_value_trend_data = []
    
    for i in range(6, -1, -1):
        date = datetime.utcnow() - timedelta(days=i)
        # Note: This is a simplified calculation. In production, you'd want to track historical values
        # For now, we'll use current stock value as baseline
        stock_value_trend_labels.append(date.strftime("%m/%d"))
        stock_value_trend_data.append(round(stock_value, 2))
    
    # Get top 5 products by quantity
    top_products = db.session.query(
        Product.name,
        Product.quantity,
        Category.name.label('category_name')
    ).join(Category, Product.category_id == Category.id, isouter=True).order_by(
        Product.quantity.desc()
    ).limit(5).all()
    
    top_products_labels = [p.name for p in top_products] if top_products else []
    top_products_data = [int(p.quantity) for p in top_products] if top_products else []
    
    # Calculate stock health metrics
    healthy_count = Product.query.filter(Product.quantity >= 20).count()
    warning_count = Product.query.filter(Product.quantity >= 10, Product.quantity < 20).count()
    critical_count = Product.query.filter(Product.quantity < 10).count()
    
    total_products = product_count if product_count > 0 else 1  # Avoid division by zero
    stock_health = {
        "healthy": healthy_count,
        "warning": warning_count,
        "critical": critical_count,
        "healthy_pct": round((healthy_count / total_products) * 100, 1),
        "warning_pct": round((warning_count / total_products) * 100, 1),
        "critical_pct": round((critical_count / total_products) * 100, 1)
    }
    
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
            # New data for enhanced charts
            "stock_value_trend_labels": stock_value_trend_labels,
            "stock_value_trend_data": stock_value_trend_data,
            "top_products_labels": top_products_labels,
            "top_products_data": top_products_data,
            "stock_health": stock_health,
        },
    )

