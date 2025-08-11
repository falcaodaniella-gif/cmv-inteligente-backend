import os
import sys
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# Inicializa o SQLAlchemy fora da função para ser acessível globalmente
db = SQLAlchemy()

def create_app():
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

    # Habilitar CORS para todas as rotas
    CORS(app)

    # Configuração do banco de dados
    # Usa DATABASE_URL do Heroku ou SQLite localmente
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL") or f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        # Importa os modelos e blueprints dentro do contexto da aplicação
        # para evitar problemas de importação circular e garantir que db esteja inicializado
        from .models.user import User
        from .models.product import Product
        from .models.supplier import Supplier
        from .models.purchase import Purchase, PurchaseItem
        from .models.inventory import Inventory, InventoryItem

        db.create_all() # Cria as tabelas no banco de dados

        # Registrar blueprints
        from .routes.user import user_bp
        from .routes.product import product_bp
        from .routes.supplier import supplier_bp
        from .routes.purchase import purchase_bp
        from .routes.inventory import inventory_bp
        from .routes.reports import reports_bp

        app.register_blueprint(user_bp, url_prefix='/api/users')
        app.register_blueprint(product_bp, url_prefix='/api/products')
        app.register_blueprint(supplier_bp, url_prefix='/api/suppliers')
        app.register_blueprint(purchase_bp, url_prefix='/api/purchases')
        app.register_blueprint(inventory_bp, url_prefix='/api/inventories')
        app.register_blueprint(reports_bp, url_prefix='/api/reports')

    # Rota para servir o frontend estático
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return "Static folder not configured", 404

        # Tenta servir o arquivo específico
        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            # Se não for um arquivo específico, serve o index.html
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return "index.html not found", 404

    return app

# A aplicação é criada aqui para ser acessível pelo Gunicorn
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
