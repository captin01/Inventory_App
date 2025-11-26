from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from sqlalchemy import func
import csv
import io
from app import db
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.routes.auth import login_required
from datetime import datetime, timedelta

bp = Blueprint("stock", __name__, url_prefix="/stock")
PER_PAGE = 200


# -----------------------------
# LIST ALL STOCK MOVEMENTS
# -----------------------------
@bp.route("/")
@login_required
def list_movements():
    # Get query parameters for filtering
    search_query = request.args.get("search", "").strip()
    movement_type = request.args.get("type", "")
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    
    # Start with base query
    query = StockMovement.query.join(Product)
    
    # Apply search filter (product name)
    if search_query:
        query = query.filter(Product.name.ilike(f"%{search_query}%"))
    
    # Apply movement type filter
    if movement_type in ["IN", "OUT"]:
        query = query.filter(StockMovement.movement_type == movement_type)
    
    # Apply date range filter
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(StockMovement.timestamp >= start)
        except ValueError:
            pass
    
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            # Add one day to include the entire end date
            end = end + timedelta(days=1)
            query = query.filter(StockMovement.timestamp < end)
        except ValueError:
            pass
    
    # Order by most recent first for display
    query = query.order_by(StockMovement.timestamp.desc(), StockMovement.id.desc())
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    movements = pagination.items
    
    # Calculate running stock for each movement
    movements_with_stock = []
    
    # For each movement, calculate what the stock was after that movement
    # by going through all movements up to that point chronologically
    for movement in movements:
        if not movement.product_id:
            movements_with_stock.append({
                "movement": movement,
                "stock_after": 0
            })
            continue
        
        # Get all movements for this product up to and including this movement (chronologically)
        all_product_movements = StockMovement.query.filter(
            StockMovement.product_id == movement.product_id,
            StockMovement.timestamp <= movement.timestamp
        ).order_by(StockMovement.timestamp.asc(), StockMovement.id.asc()).all()
        
        # Calculate stock level after this movement
        # Start with initial stock (0) and apply all movements
        stock_level = 0
        for m in all_product_movements:
            if m.movement_type == "IN":
                stock_level += m.quantity
            else:  # OUT
                stock_level -= m.quantity
        
        movements_with_stock.append({
            "movement": movement,
            "stock_after": max(0, stock_level)  # Ensure non-negative
        })
    
    return render_template(
        "stock/list.html",
        movements_data=movements_with_stock,
        pagination=pagination,
        current_search=search_query,
        current_type=movement_type,
        current_start_date=start_date,
        current_end_date=end_date,
    )


# -----------------------------
# ADD STOCK (IN)
# -----------------------------
@bp.route("/add", methods=["GET", "POST"])
@login_required
def add_stock():
    products = Product.query.all()

    if request.method == "POST":
        product_id = request.form.get("product_id")
        quantity = int(request.form.get("quantity"))

        product = Product.query.get(product_id)

        if not product:
            flash("Invalid product selected.", "danger")
            return redirect(url_for("stock.add_stock"))

        # Update product quantity
        product.quantity += quantity

        # Log movement
        movement = StockMovement(
            product_id=product.id,
            movement_type="IN",
            quantity=quantity,
            timestamp=datetime.now()
        )

        db.session.add(movement)
        db.session.add(product)  # Ensure product changes are tracked
        db.session.commit()

        flash(f"Added {quantity} units to {product.name}.", "success")
        return redirect(url_for("stock.list_movements"))

    return render_template("stock/add.html", products=products)


# -----------------------------
# REMOVE STOCK (OUT)
# -----------------------------
@bp.route("/remove", methods=["GET", "POST"])
@login_required
def remove_stock():
    products = Product.query.all()

    if request.method == "POST":
        product_id = request.form.get("product_id")
        quantity = int(request.form.get("quantity"))

        product = Product.query.get(product_id)

        if not product:
            flash("Invalid product selected.", "danger")
            return redirect(url_for("stock.remove_stock"))

        if quantity > product.quantity:
            flash("Not enough stock available!", "danger")
            return redirect(url_for("stock.remove_stock"))

        # Update product
        product.quantity -= quantity

        # Log movement
        movement = StockMovement(
            product_id=product.id,
            movement_type="OUT",
            quantity=quantity,
            timestamp=datetime.now()
        )

        db.session.add(movement)
        db.session.add(product)  # Ensure product changes are tracked
        db.session.commit()

        flash(f"Removed {quantity} units from {product.name}.", "success")
        return redirect(url_for("stock.list_movements"))

    return render_template("stock/remove.html", products=products)


@bp.route("/export")
@login_required
def export_movements():
    """Export stock movements to CSV"""
    # Get query parameters for filtering (same as list)
    search_query = request.args.get("search", "").strip()
    movement_type = request.args.get("type", "")
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    
    # Start with base query
    query = StockMovement.query.join(Product)
    
    # Apply filters (same as list view)
    if search_query:
        query = query.filter(Product.name.ilike(f"%{search_query}%"))
    
    if movement_type in ["IN", "OUT"]:
        query = query.filter(StockMovement.movement_type == movement_type)
    
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(StockMovement.timestamp >= start)
        except ValueError:
            pass
    
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            end = end + timedelta(days=1)
            query = query.filter(StockMovement.timestamp < end)
        except ValueError:
            pass
    
    # Get all movements (no pagination for export)
    movements = query.order_by(StockMovement.timestamp.desc(), StockMovement.id.desc()).all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['ID', 'Product Name', 'Product SKU', 'Movement Type', 'Quantity', 'Date/Time', 'Stock After'])
    
    # Write data
    for movement in movements:
        # Calculate stock after for this movement
        if movement.product_id:
            all_product_movements = StockMovement.query.filter(
                StockMovement.product_id == movement.product_id,
                StockMovement.timestamp <= movement.timestamp
            ).order_by(StockMovement.timestamp.asc(), StockMovement.id.asc()).all()
            
            stock_level = 0
            for m in all_product_movements:
                if m.movement_type == "IN":
                    stock_level += m.quantity
                else:
                    stock_level -= m.quantity
            stock_after = max(0, stock_level)
        else:
            stock_after = 0
        
        writer.writerow([
            movement.id,
            movement.product.name if movement.product else 'Unknown',
            movement.product.sku if movement.product else 'N/A',
            movement.movement_type,
            movement.quantity,
            movement.timestamp.strftime('%Y-%m-%d %H:%M:%S') if movement.timestamp else 'N/A',
            stock_after
        ])
    
    # Create response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=stock_movements_export.csv'}
    )
