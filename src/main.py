from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, static_folder=\'../cmv-frontend/dist\', static_url_path=\'/\')
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") or "sqlite:///database/app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    CORS(app)

    with app.app_context():
        # Import models here to avoid circular imports
        from .models.user import User
        from .models.product import Product
        from .models.supplier import Supplier
        from .models.purchase import Purchase, PurchaseItem
        from .models.inventory import Inventory, InventoryItem

        db.create_all()

        # Register blueprints
        from .routes.user import user_bp
        from .routes.product import product_bp
        from .routes.supplier import supplier_bp
        from .routes.purchase import purchase_bp
        from .routes.inventory import inventory_bp
        from .routes.reports import reports_bp

        app.register_blueprint(user_bp, url_prefix=\\'/api/users\\')
        app.register_blueprint(product_bp, url_prefix=\\'/api/products\\')
        app.register_blueprint(supplier_bp, url_prefix=\\'/api/suppliers\\')
        app.register_blueprint(purchase_bp, url_prefix=\\'/api/purchases\\')
        app.register_blueprint(inventory_bp, url_prefix=\\'/api/inventories\\')
        app.register_blueprint(reports_bp, url_prefix=\\'/api/reports\\')

    @app.route(\'/\')
    def serve_index():
        try:
            return send_from_directory(app.static_folder, \'index.html\')
        except Exception as e:
            print(f"Error serving index.html: {e}")
            return "index.html not found", 404

    return app

# A aplicação é criada aqui para ser acessível pelo Gunicorn
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
