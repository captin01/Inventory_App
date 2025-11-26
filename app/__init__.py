from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from .config import Config


db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class: type[Config] = Config) -> Flask:
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS
    CORS(app)

    # Initialize DB and migrations
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so SQLAlchemy recognizes them
    from app.models.category import Category
    from app.models.product import Product
    from app.models.stock_movement import StockMovement
    from app.models.user import User
    
    
    
    # Register blueprints
    from .routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.category import bp as category_bp
    app.register_blueprint(category_bp)

    from app.routes.product import bp as product_bp
    app.register_blueprint(product_bp)

    from app.routes.stock import bp as stock_bp
    app.register_blueprint(stock_bp)

    
    # Shell context (for flask shell)
    @app.shell_context_processor
    def make_shell_context():
        return {
            "db": db,
            "Category": Category,
            "Product": Product,
            "StockMovement": StockMovement,
        }

    return app
