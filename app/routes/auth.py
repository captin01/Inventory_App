from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models.user import User
from functools import wraps

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


@bp.route("/login", methods=["GET", "POST"])
def login():
    """User login route."""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template("auth/login.html")

        # Find user by email
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash("Your account has been deactivated. Please contact an administrator.", "danger")
                return render_template("auth/login.html")

            # Set session
            session["user_id"] = user.id
            session["user_email"] = user.email
            session["user_name"] = user.full_name
            session["user_role"] = user.role

            flash(f"Welcome back, {user.full_name}!", "success")
            next_page = request.args.get("next") or url_for("main.home")
            return redirect(next_page)
        else:
            flash("Invalid email or password.", "danger")

    return render_template("auth/login.html")


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    """User registration route."""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        full_name = request.form.get("full_name", "").strip()

        # Validation
        errors = []
        if not email:
            errors.append("Email is required.")
        elif "@" not in email:
            errors.append("Please enter a valid email address.")
        elif User.query.filter_by(email=email).first():
            errors.append("An account with this email already exists.")

        if not password:
            errors.append("Password is required.")
        elif len(password) < 8:
            errors.append("Password must be at least 8 characters long.")

        if password != confirm_password:
            errors.append("Passwords do not match.")

        if not full_name:
            errors.append("Full name is required.")

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("auth/signup.html")

        # Create new user
        try:
            user = User(
                email=email,
                full_name=full_name,
                role="staff",  # Default role
                is_active=True
            )
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while creating your account. Please try again.", "danger")
            return render_template("auth/signup.html")

    return render_template("auth/signup.html")


@bp.route("/logout")
def logout():
    """User logout route."""
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("main.landing"))


@bp.route("/check")
def check_auth():
    """Check if user is authenticated (for testing)."""
    if "user_id" in session:
        return {
            "authenticated": True,
            "user_id": session.get("user_id"),
            "email": session.get("user_email"),
            "name": session.get("user_name"),
            "role": session.get("user_role")
        }
    return {"authenticated": False}

