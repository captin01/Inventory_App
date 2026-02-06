import os
# 'dotenv' helps load environment variables (like database passwords) from a .env file
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Import the application factory and database object from our app package
from app import create_app, db
# Import the User model so we can query and modify user data
from app.models.user import User
# Import specific database errors to handle connection issues gracefully
from sqlalchemy.exc import OperationalError, ProgrammingError

def reset_admin():
    print("Initializing application context...")
    
    # 1. Create the Flask application instance
    # This loads the configuration (including database URI) from config.py
    app = create_app()
    
    # Debug: Print the Database URI being used
    # This helps confirm if we are connecting to localhost, a specific port, etc.
    # Note: app.config.get() fetches values from the loaded configuration
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    print(f"Using Database URI: {db_uri}")

    try:
        # 2. Enter the Application Context
        # Flask-SQLAlchemy needs to know which 'app' it is working with to access the database.
        # The 'with' statement ensures the context is set up and torn down correctly.
        with app.app_context():
            
            # 3. Test Database Connection
            print("Connecting to database...")
            try:
                # Query all users to check if the connection works
                users = User.query.all()
                print(f"Connection successful. Found {len(users)} users in the database.")
            except (OperationalError, ProgrammingError) as e:
                # If we catch an error here, it usually means credentials are wrong
                # or the database server isn't running.
                print("\n!!! DATABASE CONNECTION ERROR !!!")
                print(f"Error details: {e}")
                print("\nPossible solutions:")
                print("1. Ensure your MySQL server is running.")
                print("2. Check if your DATABASE_URL environment variable is set correctly.")
                print("3. If you are using a .env file, make sure it is valid.")
                print("4. You can manually edit app/config.py to set the correct username/password.")
                return

            # 4. Search for an Admin User
            admin_found = False
            
            # Loop through all existing users
            for user in users:
                print(f"User: {user.email} (Role: {user.role})")
                
                # Check if this user has 'admin' privileges
                if user.role == 'admin':
                    admin_found = True
                    print(f"--> Resetting password for admin user: {user.email}")
                    
                    # 5. Reset Password
                    # This uses the set_password method on the User model trying to hash 'admin123'
                    user.set_password("admin123")
                    
                    # Commit (save) the changes to the database
                    db.session.commit()
                    print(f"SUCCESS: Password for {user.email} has been reset to 'admin123'")
            
            # 6. Create New Admin if None Found
            if not admin_found:
                print("No admin user found. Creating one...")
                admin_email = "admin@example.com"
                try:
                    # Create a new User instance
                    new_admin = User(
                        email=admin_email,
                        full_name="System Admin",
                        role="admin",     # Important: Set role to admin
                        is_active=True
                    )
                    # Hash the password
                    new_admin.set_password("admin123")
                    
                    # Add to the session and commit
                    db.session.add(new_admin)
                    db.session.commit()
                    print(f"SUCCESS: Created new admin user '{admin_email}' with password 'admin123'")
                except Exception as e:
                     print(f"Error creating user: {e}")
                     print("Maybe the email already exists?")

    except Exception as e:
        # Catch-all for any other unexpected errors (e.g., code bugs)
        print(f"An unexpected error occurred: {e}")

# This block allows the script to be run directly from the terminal
if __name__ == "__main__":
    reset_admin()
