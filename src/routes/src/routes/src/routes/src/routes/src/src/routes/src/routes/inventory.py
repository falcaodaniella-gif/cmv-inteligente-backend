from flask import Blueprint, request, jsonify
from ..main import db
from ..models.inventory import Inventory, InventoryItem
from ..models.product import Product
from datetime import datetime

inventory_bp = Blueprint(\'inventory_bp\', __name__)

@inventory_bp.route(\'/\', methods=[\'POST\
])
def add_inventory():
    data = request.get_json()
    if not data or not \'date\' in data or not \'items\' in data:
        return jsonify({\'error\': \'Missing data\'}), 400

    try:
        inventory_date = datetime.strptime(data[\'date\
'], \'%Y-%m-%d\').date()
    except ValueError:
        return jsonify({\'error\': \'Invalid date format. Use YYYY-MM-DD\'}), 400

    new_inventory = Inventory(date=inventory_date)
    db.session.add(new_inventory)
    db.session.flush() # To get the inventory ID before committing

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

        if quantity < 0:
            db.session.rollback()
            return jsonify({\'error\': \'Quantity cannot be negative\'}), 400

        new_item = InventoryItem(
            inventory_id=new_inventory.id,
            product_id=item_data[\'product_id\
'],
            quantity=quantity
        )
        db.session.add(new_item)
    
    db.session.commit()

    # Fetch the inventory again to include product names in items
    inventory_with_items = Inventory.query.get(new_inventory.id)
    items_output = []
    for item in inventory_with_items.items:
        items_output.append({
            \'id\': item.id,
            \'product_id\': item.product_id,
            \'product_name\': item.product.name,
            \'quantity\': item.quantity
        })

    return jsonify({
        \'id\': inventory_with_items.id,
        \'date\': inventory_with_items.date.strftime(\'%Y-%m-%d\
'),
        \'items\': items_output
    }), 201

@inventory_bp.route(\'/\', methods=[\'GET\
])
def get_inventories():
    inventories = Inventory.query.all()
    output = []
    for inventory in inventories:
        items_output = []
        for item in inventory.items:
            items_output.append({
                \'id\': item.id,
                \'product_id\': item.product_id,
                \'product_name\': item.product.name,
                \'quantity\': item.quantity
            })
        output.append({
            \'id\': inventory.id,
            \'date\': inventory.date.strftime(\'%Y-%m-%d\
'),
            \'items\': items_output
        })
    return jsonify(output)

@inventory_bp.route(\'/<int:inventory_id>\', methods=[\'GET\
])
def get_inventory(inventory_id):
    inventory = Inventory.query.get_or_404(inventory_id)
    items_output = []
    for item in inventory.items:
        items_output.append({
            \'id\': item.id,
            \'product_id\': item.product_id,
            \'product_name\': item.product.name,
            \'quantity\': item.quantity
        })
    return jsonify({
        \'id\': inventory.id,
        \'date\': inventory.date.strftime(\'%Y-%m-%d\
'),
        \'items\': items_output
    })

@inventory_bp.route(\'/<int:inventory_id>\', methods=[\'DELETE\
])
def delete_inventory(inventory_id):
    inventory = Inventory.query.get_or_404(inventory_id)
    db.session.delete(inventory)
    db.session.commit()
    return jsonify({\'message\': \'Inventory deleted successfully\'}), 200
