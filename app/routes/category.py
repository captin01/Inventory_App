from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from sqlalchemy import func
import csv
import io
from app import db
from app.models.category import Category
from app.models.product import Product
from app.routes.auth import login_required

bp = Blueprint("category", __name__, url_prefix="/categories")
PER_PAGE = 200


@bp.route("/")
@login_required
def list_categories():
    # Get query parameters for filtering and sorting
    search_query = request.args.get("search", "").strip()
    sort_by = request.args.get("sort", "name")
    
    # Start with base query
    query = Category.query
    
    # Apply search filter
    if search_query:
        query = query.filter(Category.name.ilike(f"%{search_query}%"))
    
    # Apply sorting
    if sort_by == "name":
        query = query.order_by(Category.name.asc())
    elif sort_by == "most_products":
        # Order by product count (descending)
        query = query.outerjoin(Product).group_by(Category.id).order_by(func.count(Product.id).desc())
    elif sort_by == "recently_added":
        # Assuming we might add created_at later, for now just by ID desc
        query = query.order_by(Category.id.desc())
    else:
        query = query.order_by(Category.name.asc())
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    categories = pagination.items
    
    # Get product counts for each category
    category_data = []
    for category in categories:
        product_count = Product.query.filter_by(category_id=category.id).count()
        category_data.append({
            "category": category,
            "product_count": product_count
        })
    
    return render_template(
        "categories/list.html",
        category_data=category_data,
        pagination=pagination,
        current_search=search_query,
        current_sort=sort_by,
    )


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create_category():
    if request.method == "POST":
        name = request.form.get("name")

        if not name:
            flash("Category name is required", "error")
            return redirect(url_for("category.create_category"))

        new_cat = Category(name=name)
        db.session.add(new_cat)
        db.session.commit()

        flash("Category created successfully!", "success")
        return redirect(url_for("category.list_categories"))

    return render_template("categories/create.html")


@bp.route("/edit/<int:cat_id>", methods=["GET", "POST"])
@login_required
def edit_category(cat_id):
    cat = Category.query.get_or_404(cat_id)

    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            flash("Name cannot be empty", "error")
            return redirect(url_for("category.edit_category", cat_id=cat_id))

        cat.name = name
        db.session.commit()

        flash("Category updated!", "success")
        return redirect(url_for("category.list_categories"))

    return render_template("categories/edit.html", category=cat)


@bp.route("/delete/<int:cat_id>", methods=["POST"])
@login_required
def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    db.session.delete(cat)
    db.session.commit()

    flash("Category deleted!", "success")
    return redirect(url_for("category.list_categories"))


@bp.route("/export")
@login_required
def export_categories():
    """Export categories to CSV"""
    # Get all categories
    categories = Category.query.order_by(Category.name.asc()).all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['ID', 'Name', 'Description', 'Product Count'])
    
    # Write data
    for category in categories:
        product_count = Product.query.filter_by(category_id=category.id).count()
        writer.writerow([
            category.id,
            category.name,
            category.description or '',
            product_count
        ])
    
    # Create response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=categories_export.csv'}
    )
