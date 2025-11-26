from app import create_app

# IMPORTANT — force Flask to load all modules inside app.routes
import app.routes.stock
import app.routes.product
import app.routes.category
import app.routes.main

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
