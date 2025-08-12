import os
from flask import Flask, jsonify
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    
    # Habilitar CORS
    CORS(app)
    
    # Rota de teste simples
    @app.route('/')
    def home():
        return jsonify({
            "message": "CMV Inteligente - Backend funcionando!",
            "status": "success"
        })
    
    @app.route('/api/products')
    def get_products():
        return jsonify([])
    
    @app.route('/api/suppliers')
    def get_suppliers():
        return jsonify([])
    
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy"})
    
    return app

# Criar a aplicação
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
