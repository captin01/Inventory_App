#!/usr/bin/env python3
"""
Secure Admin Creation Script

This script creates an admin user for the inventory management system.
It uses environment variables for security and prevents hard-coding passwords.

Requirements:
- ADMIN_PASSWORD environment variable must be set
- ADMIN_EMAIL environment variable (optional, defaults to 'admin@example.com')
- ADMIN_NAME environment variable (optional, defaults to 'Administrator')

Usage:
    export ADMIN_PASSWORD="your-secure-password"
    python scripts/create_admin.py
"""

import os
import sys
from pathlib import Path
from werkzeug.security import generate_password_hash

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app, db
from datetime import datetime


# Define User model inline (in case it doesn't exist in models yet)
class User(db.Model):
    """User model for authentication and role-based access."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="staff")
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<User {self.email}>"


def get_admin_password():
    """
    Get admin password from environment variable.
    Prevents hard-coding passwords in the script.
    """
    password = os.getenv("ADMIN_PASSWORD")
    if not password:
        print("❌ ERROR: ADMIN_PASSWORD environment variable is not set!")
        print("\nPlease set it before running this script:")
        print("  Windows (PowerShell): $env:ADMIN_PASSWORD='your-password'")
        print("  Windows (CMD): set ADMIN_PASSWORD=your-password")
        print("  Linux/Mac: export ADMIN_PASSWORD='your-password'")
        sys.exit(1)
    
    if len(password) < 8:
        print("⚠️  WARNING: Password is less than 8 characters. Consider using a stronger password.")
    
    return password


def admin_exists(app):
    """Check if an admin user already exists in the database."""
    with app.app_context():
        try:
            admin = User.query.filter_by(role="admin").first()
            return admin is not None
        except Exception as e:
            # Table might not exist yet
            print(f"⚠️  Note: Could not check for existing admin: {e}")
            return False


def create_admin_user(app):
    """
    Create admin user if it doesn't already exist.
    Uses environment variables for all sensitive data.
    """
    # Get configuration from environment variables
    password = get_admin_password()
    email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    full_name = os.getenv("ADMIN_NAME", "Administrator")
    
    with app.app_context():
        # Check if admin already exists
        if admin_exists(app):
            print("✓ Admin user already exists. Skipping creation.")
            admin = User.query.filter_by(role="admin").first()
            print(f"  Existing admin: {admin.email} ({admin.full_name})")
            return False
        
        # Ensure users table exists
        try:
            db.create_all()
        except Exception as e:
            print(f"⚠️  Note: {e}")
        
        # Check if user with this email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"❌ ERROR: User with email '{email}' already exists!")
            print(f"   Existing user role: {existing_user.role}")
            sys.exit(1)
        
        # Create new admin user
        try:
            password_hash = generate_password_hash(password)
            admin = User(
                email=email,
                password_hash=password_hash,
                full_name=full_name,
                role="admin",
                is_active=True
            )
            
            db.session.add(admin)
            db.session.commit()
            
            print("✓ Admin user created successfully!")
            print(f"  Email: {email}")
            print(f"  Name: {full_name}")
            print(f"  Role: admin")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ ERROR: Failed to create admin user: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Main execution function."""
    print("=" * 60)
    print("Admin User Creation Script")
    print("=" * 60)
    print()
    
    # Verify environment variable is set
    if not os.getenv("ADMIN_PASSWORD"):
        get_admin_password()  # This will exit with error message
    
    # Create Flask app
    try:
        app = create_app()
        print("✓ Flask app initialized")
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize Flask app: {e}")
        sys.exit(1)
    
    print()
    
    # Create admin user
    create_admin_user(app)
    
    print()
    print("=" * 60)
    print("Script completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

