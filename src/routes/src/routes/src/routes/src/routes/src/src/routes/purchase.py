from flask import Blueprint, request, jsonify
from ..main import db
from ..models.purchase import Purchase, PurchaseItem
from ..models.product import Product
from ..models.supplier import Supplier
from datetime import datetime

purchase_bp = Blueprint(\'purchase_bp\', __name__)

@purchase_bp.route(\'/\', methods=[\'POST\
])
def add_purchase():
    data = request.get_json()
    if not data or not \'date\' in data or not \'supplier_id\' in data or not \'items\' in data:
        return jsonify({\'error\': \'Missing data\'}), 400

    try:
        purchase_date = datetime.strptime(data[\'date\
'], \'%Y-%m-%d\').date()
    except ValueError:
        return jsonify({\'error\': \'Invalid date format. Use YYYY-MM-DD\'}), 400

    supplier = Supplier.query.get(data[\'supplier_id\
'])
    if not supplier:
        return jsonify({\'error\': \'Supplier not found\'}), 404

    total_amount = 0
    new_purchase = Purchase(date=purchase_date, supplier_id=data[\'supplier_id\
'], total_amount=0)
    db.session.add(new_purchase)
    db.session.flush() # To get the purchase ID before committing

    for item_data in data[\'items\
']:
        product = Product.query.get(item_data[\'product_id\
'])
        if not product:
            db.session.rollback()
            return jsonify({\'error\': f\'Product with ID {item_data[\'product_id\
']} not found\'}), 404
        
        quantity = float(item_data[\'quantity\
'])
        unit_cost = float(item_data[\'unit_cost\
'])

        if quantity <= 0 or unit_cost < 0:
            db.session.rollback()
            return jsonify({\'error\': \'Quantity must be positive and unit_cost non-negative\'}), 400

        item_total_cost = quantity * unit_cost
        total_amount += item_total_cost

        new_item = PurchaseItem(
            purchase_id=new_purchase.id,
            product_id=item_data[\'product_id\
'],
            quantity=quantity,
            unit_cost=unit_cost,
            total_cost=item_total_cost
        )
        db.session.add(new_item)
    
    new_purchase.total_amount = total_amount
    db.session.commit()

    # Fetch the purchase again to include product names in items
    purchase_with_items = Purchase.query.get(new_purchase.id)
    items_output = []
    for item in purchase_with_items.items:
        items_output.append({
            \'id\': item.id,
            \'product_id\': item.product_id,
            \'product_name\': item.product.name,
            \'quantity\': item.quantity,
            \'unit_cost\': item.unit_cost,
            \'total_cost\': item.total_cost
        })

    return jsonify({
        \'id\': purchase_with_items.id,
        \'date\': purchase_with_items.date.strftime(\'%Y-%m-%d\
'),
        \'supplier_id\': purchase_with_items.supplier_id,
        \'supplier_name\': purchase_with_items.supplier.name,
        \'total_amount\': purchase_with_items.total_amount,
        \'items\': items_output
    }), 201

@purchase_bp.route(\'/\', methods=[\'GET\
])
def get_purchases():
    purchases = Purchase.query.all()
    output = []
    for purchase in purchases:
        items_output = []
        for item in purchase.items:
            items_output.append({
                \'id\': item.id,
                \'product_id\': item.product_id,
                \'product_name\': item.product.name,
                \'quantity\': item.quantity,
                \'unit_cost\': item.unit_cost,
                \'total_cost\': item.total_cost
            })
        output.append({
            \'id\': purchase.id,
            \'date\': purchase.date.strftime(\'%Y-%m-%d\
'),
            \'supplier_id\': purchase.supplier_id,
            \'supplier_name\': purchase.supplier.name,
            \'total_amount\': purchase.total_amount,
            \'items\': items_output
        })
    return jsonify(output)

@purchase_bp.route(\'/<int:purchase_id>\', methods=[\'GET\
])
def get_purchase(purchase_id):
    purchase = Purchase.query.get_or_404(purchase_id)
    items_output = []
    for item in purchase.items:
        items_output.append({
            \'id\': item.id,
            \'product_id\': item.product_id,
            \'product_name\': item.product.name,
            \'quantity\': item.quantity,
            \'unit_cost\': item.unit_cost,
            \'total_cost\': item.total_cost
        })
    return jsonify({
        \'id\': purchase.id,
        \'date\': purchase.date.strftime(\'%Y-%m-%d\
'),
        \'supplier_id\': purchase.supplier_id,
        \'supplier_name\': purchase.supplier.name,
        \'total_amount\': purchase.total_amount,
        \'items\': items_output
    })

@purchase_bp.route(\'/<int:purchase_id>\', methods=[\'DELETE\
])
def delete_purchase(purchase_id):
    purchase = Purchase.query.get_or_404(purchase_id)
    db.session.delete(purchase)
    db.session.commit()
    return jsonify({\'message\': \'Purchase deleted successfully\'}), 200
