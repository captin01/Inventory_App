from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
import csv
import io
from app import db
from app.models.product import Product
from app.models.category import Category
from app.routes.auth import login_required

bp = Blueprint("product", __name__, url_prefix="/products")
PER_PAGE = 200


@bp.route("/")
@login_required
def list_products():
    # Get all categories for filter dropdown
    categories = Category.query.all()
    
    # Get query parameters for filtering
    search_query = request.args.get("search", "").strip()
    category_filter = request.args.get("category", type=int)
    stock_filter = request.args.get("stock", "")
    
    # Start with base query
    query = Product.query
    
    # Apply search filter
    if search_query:
        query = query.filter(
            (Product.name.ilike(f"%{search_query}%")) |
            (Product.sku.ilike(f"%{search_query}%"))
        )
    
    # Apply category filter
    if category_filter:
        query = query.filter(Product.category_id == category_filter)
    
    # Apply stock status filter
    if stock_filter == "in_stock":
        query = query.filter(Product.quantity > 0)
    elif stock_filter == "low_stock":
        query = query.filter(Product.quantity > 0, Product.quantity < 10)
    elif stock_filter == "out_of_stock":
        query = query.filter(Product.quantity == 0)
    
    # Order by created date (newest first)
    query = query.order_by(Product.created_at.desc())
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    products = pagination.items
    
    return render_template(
        "products/list.html",
        products=products,
        pagination=pagination,
        categories=categories,
        current_search=search_query,
        current_category=category_filter,
        current_stock=stock_filter,
    )


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create_product():
    categories = Category.query.all()

    if request.method == "POST":
        name = request.form.get("name")
        sku = request.form.get("sku")
        price = request.form.get("price", type=float)
        quantity = request.form.get("quantity", type=int)
        category_id = request.form.get("category_id", type=int)

        if not all([name, sku, price is not None, quantity is not None, category_id]):
            flash("All fields are required.", "error")
            return redirect(url_for("product.create_product"))

        product = Product(
            name=name,
            sku=sku,
            price=price,
            quantity=quantity,
            category_id=category_id
        )
        db.session.add(product)
        db.session.commit()

        flash("Product created successfully!", "success")
        return redirect(url_for("product.list_products"))

    return render_template("products/create.html", categories=categories)


@bp.route("/edit/<int:prod_id>", methods=["GET", "POST"])
@login_required
def edit_product(prod_id):
    product = Product.query.get_or_404(prod_id)
    categories = Category.query.all()

    if request.method == "POST":
        product.name = request.form.get("name")
        product.sku = request.form.get("sku")
        product.price = request.form.get("price", type=float)
        product.quantity = request.form.get("quantity", type=int)
        product.category_id = request.form.get("category_id", type=int)

        db.session.commit()
        flash("Product updated!", "success")
        return redirect(url_for("product.list_products"))

    return render_template("products/edit.html", product=product, categories=categories)


@bp.route("/delete/<int:prod_id>", methods=["POST"])
@login_required
def delete_product(prod_id):
    product = Product.query.get_or_404(prod_id)
    db.session.delete(product)
    db.session.commit()

    flash("Product deleted!", "success")
    return redirect(url_for("product.list_products"))


@bp.route("/export")
@login_required
def export_products():
    """Export products to CSV"""
    # Get all products (no pagination for export)
    products = Product.query.order_by(Product.created_at.desc()).all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['ID', 'Name', 'SKU', 'Category', 'Price', 'Quantity', 'Created At'])
    
    # Write data
    for product in products:
        writer.writerow([
            product.id,
            product.name,
            product.sku,
            product.category.name if product.category else 'N/A',
            product.price,
            product.quantity,
            product.created_at.strftime('%Y-%m-%d %H:%M:%S') if product.created_at else 'N/A'
        ])
    
    # Create response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=products_export.csv'}
    )
