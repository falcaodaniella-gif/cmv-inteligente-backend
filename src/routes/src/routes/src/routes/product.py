from flask import Blueprint, request, jsonify
from ..main import db
from ..models.product import Product

product_bp = Blueprint(\'product_bp\', __name__)

@product_bp.route(\'/\', methods=[\'POST\
])
def add_product():
    data = request.get_json()
    if not data or not \'name\' in data or not \'unit\' in data or not \'category\' in data:
        return jsonify({\'error\': \'Missing data\'}), 400
    
    new_product = Product(name=data[\'name\
'], unit=data[\'unit\
'], category=data[\'category\
'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({
        \'id\': new_product.id,
        \'name\': new_product.name,
        \'unit\': new_product.unit,
        \'category\': new_product.category
    }), 201

@product_bp.route(\'/\', methods=[\'GET\
])
def get_products():
    products = Product.query.all()
    output = []
    for product in products:
        output.append({
            \'id\': product.id,
            \'name\': product.name,
            \'unit\': product.unit,
            \'category\': product.category
        })
    return jsonify(output)

@product_bp.route(\'/<int:product_id>\', methods=[\'GET\
])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        \'id\': product.id,
        \'name\': product.name,
        \'unit\': product.unit,
        \'category\': product.category
    })

@product_bp.route(\'/<int:product_id>\', methods=[\'PUT\
])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    if not data:
        return jsonify({\'error\': \'No data provided\'}), 400

    product.name = data.get(\'name\', product.name)
    product.unit = data.get(\'unit\', product.unit)
    product.category = data.get(\'category\', product.category)
    db.session.commit()
    return jsonify({
        \'id\': product.id,
        \'name\': product.name,
        \'unit\': product.unit,
        \'category\': product.category
    })

@product_bp.route(\'/<int:product_id>\', methods=[\'DELETE\
])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({\'message\': \'Product deleted successfully\'}), 200
