from flask import Blueprint, request, jsonify
from ..main import db
from ..models.product import Product
from ..models.purchase import Purchase, PurchaseItem
from ..models.inventory import Inventory, InventoryItem
from datetime import datetime, timedelta
from sqlalchemy import func, and_

reports_bp = Blueprint(\'reports_bp\', __name__)

@reports_bp.route(\'/cmv\', methods=[\'GET\
])
def calculate_cmv():
    start_date_str = request.args.get(\'start_date\')
    end_date_str = request.args.get(\'end_date\')

    if not start_date_str or not end_date_str:
        return jsonify({\'error\': \'Please provide start_date and end_date\'}), 400

    try:
        start_date = datetime.strptime(start_date_str, \'%Y-%m-%d\').date()
        end_date = datetime.strptime(end_date_str, \'%Y-%m-%d\').date()
    except ValueError:
        return jsonify({\'error\': \'Invalid date format. Use YYYY-MM-DD\'}), 400

    # Get all products
    products = Product.query.all()
    cmv_results = []
    total_cmv = 0

    for product in products:
        # 1. Estoque Inicial (EI): Último inventário antes da data de início
        initial_inventory = Inventory.query.filter(
            Inventory.date < start_date
        ).order_by(Inventory.date.desc()).first()

        ei_quantity = 0
        if initial_inventory:
            ei_item = InventoryItem.query.filter_by(
                inventory_id=initial_inventory.id,
                product_id=product.id
            ).first()
            if ei_item: 
                ei_quantity = ei_item.quantity
        
        # 2. Compras (C): Compras do produto dentro do período
        purchases_in_period = db.session.query(func.sum(PurchaseItem.quantity), func.sum(PurchaseItem.total_cost)).filter(
            and_(
                PurchaseItem.product_id == product.id,
                Purchase.id == PurchaseItem.purchase_id,
                Purchase.date >= start_date,
                Purchase.date <= end_date
            )
        ).first()

        purchases_quantity = purchases_in_period[0] if purchases_in_period[0] else 0
        purchases_cost = purchases_in_period[1] if purchases_in_period[1] else 0

        # 3. Estoque Final (EF): Último inventário até a data de fim
        final_inventory = Inventory.query.filter(
            Inventory.date <= end_date
        ).order_by(Inventory.date.desc()).first()

        ef_quantity = 0
        if final_inventory:
            ef_item = InventoryItem.query.filter_by(
                inventory_id=final_inventory.id,
                product_id=product.id
            ).first()
            if ef_item:
                ef_quantity = ef_item.quantity

        # Calcular Custo Médio Ponderado (CMP) para o período
        # Se não houver compras no período, mas houver estoque inicial, usar o custo do estoque inicial
        # Isso é uma simplificação. Em um sistema real, o CMP seria mais complexo.
        if purchases_quantity > 0:
            average_cost_per_unit = purchases_cost / purchases_quantity
        elif ei_quantity > 0: # Se não houve compras, mas tinha estoque inicial, assumir custo 0 para simplificar
            average_cost_per_unit = 0 # Ou buscar o custo do inventário inicial se disponível
        else:
            average_cost_per_unit = 0

        # Calcular Consumo (CMV em quantidade)
        consumed_quantity = ei_quantity + purchases_quantity - ef_quantity
        if consumed_quantity < 0: # Evitar CMV negativo por erro de inventário
            consumed_quantity = 0

        # Calcular CMV em valor
        cmv_value = consumed_quantity * average_cost_per_unit
        total_cmv += cmv_value

        cmv_results.append({
            \'product_id\': product.id,
            \'product_name\': product.name,
            \'initial_stock\': ei_quantity,
            \'purchases_quantity\': purchases_quantity,
            \'final_stock\': ef_quantity,
            \'consumed_quantity\': consumed_quantity,
            \'cmv\': round(cmv_value, 2) # Arredondar para 2 casas decimais
        })
    
    # Sort by CMV value in descending order
    cmv_results.sort(key=lambda x: x[\'cmv\
'], reverse=True)

    return jsonify({
        \'period\': {
            \'start_date\': start_date.strftime(\'%Y-%m-%d\
'),
            \'end_date\': end_date.strftime(\'%Y-%m-%d\
')
        },
        \'total_cmv\': round(total_cmv, 2),
        \'products\': cmv_results
    })

@reports_bp.route(\'/purchase_list\', methods=[\'GET\
])
def generate_purchase_list():
    inventory_id = request.args.get(\'inventory_id\')
    if not inventory_id:
        return jsonify({\'error\': \'Please provide an inventory_id\'}), 400

    inventory = Inventory.query.get(inventory_id)
    if not inventory:
        return jsonify({\'error\': \'Inventory not found\'}), 404

    # Get the previous inventory to calculate consumption
    previous_inventory = Inventory.query.filter(
        Inventory.date < inventory.date
    ).order_by(Inventory.date.desc()).first()

    # Get purchases between previous and current inventory
    purchases_between_inventories = db.session.query(PurchaseItem).join(Purchase).filter(
        and_(
            Purchase.date > previous_inventory.date if previous_inventory else \'1\'==\'1\', # If no previous, consider all purchases before current
            Purchase.date <= inventory.date
        )
    ).all()

    # Calculate current stock based on current inventory
    current_stock = {item.product_id: item.quantity for item in inventory.items}

    # Calculate consumption (simplified: initial + purchases - final)
    # This needs to be more robust for a real system, considering recipes and sales
    product_consumption = {}
    all_products = Product.query.all()

    for product in all_products:
        ei = 0
        if previous_inventory:
            prev_item = next((item for item in previous_inventory.items if item.product_id == product.id), None)
            if prev_item: ei = prev_item.quantity
        
        purchases_qty = sum([item.quantity for item in purchases_between_inventories if item.product_id == product.id])
        
        ef = current_stock.get(product.id, 0)

        consumption = ei + purchases_qty - ef
        if consumption > 0: # Only consider positive consumption for purchase suggestions
            product_consumption[product.id] = consumption

    purchase_suggestions = []
    total_estimated_cost = 0

    for product_id, consumption in product_consumption.items():
        product = Product.query.get(product_id)
        if product:
            # Simplified: suggest buying what was consumed
            suggested_quantity = consumption
            
            # Get last purchase price for estimated cost
            last_purchase_item = PurchaseItem.query.filter_by(product_id=product.id).join(Purchase).order_by(Purchase.date.desc()).first()
            estimated_unit_cost = last_purchase_item.unit_cost if last_purchase_item else 0
            estimated_cost = suggested_quantity * estimated_unit_cost
            total_estimated_cost += estimated_cost

            purchase_suggestions.append({
                \'product_id\': product.id,
                \'product_name\': product.name,
                \'current_stock\': current_stock.get(product.id, 0),
                \'consumption\': round(consumption, 2),
                \'suggested_quantity\': round(suggested_quantity, 2),
                \'estimated_unit_cost\': round(estimated_unit_cost, 2),
                \'estimated_cost\': round(estimated_cost, 2)
            })
    
    purchase_suggestions.sort(key=lambda x: x[\'estimated_cost\
'], reverse=True)

    return jsonify({
        \'inventory_id\': inventory.id,
        \'inventory_date\': inventory.date.strftime(\'%Y-%m-%d\
'),
        \'total_estimated_cost\': round(total_estimated_cost, 2),
        \'items\': purchase_suggestions
    })
