from flask import Blueprint, request, jsonify
from ..main import db
from ..models.supplier import Supplier

supplier_bp = Blueprint(\'supplier_bp\', __name__)

@supplier_bp.route(\'/\', methods=[\'POST\
])
def add_supplier():
    data = request.get_json()
    if not data or not \'name\' in data:
        return jsonify({\'error\': \'Missing supplier name\'}), 400
    
    new_supplier = Supplier(name=data[\'name\
'], contact_info=data.get(\'contact_info\'))
    db.session.add(new_supplier)
    db.session.commit()
    return jsonify({
        \'id\': new_supplier.id,
        \'name\': new_supplier.name,
        \'contact_info\': new_supplier.contact_info
    }), 201

@supplier_bp.route(\'/\', methods=[\'GET\
])
def get_suppliers():
    suppliers = Supplier.query.all()
    output = []
    for supplier in suppliers:
        output.append({
            \'id\': supplier.id,
            \'name\': supplier.name,
            \'contact_info\': supplier.contact_info
        })
    return jsonify(output)

@supplier_bp.route(\'/<int:supplier_id>\', methods=[\'GET\
])
def get_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    return jsonify({
        \'id\': supplier.id,
        \'name\': supplier.name,
        \'contact_info\': supplier.contact_info
    })

@supplier_bp.route(\'/<int:supplier_id>\', methods=[\'PUT\
])
def update_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    data = request.get_json()
    if not data:
        return jsonify({\'error\': \'No data provided\'}), 400

    supplier.name = data.get(\'name\', supplier.name)
    supplier.contact_info = data.get(\'contact_info\', supplier.contact_info)
    db.session.commit()
    return jsonify({
        \'id\': supplier.id,
        \'name\': supplier.name,
        \'contact_info\': supplier.contact_info
    })

@supplier_bp.route(\'/<int:supplier_id>\', methods=[\'DELETE\
])
def delete_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    db.session.delete(supplier)
    db.session.commit()
    return jsonify({\'message\': \'Supplier deleted successfully\'}), 200
