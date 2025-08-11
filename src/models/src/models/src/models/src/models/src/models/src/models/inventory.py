from ..main import db

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    items = db.relationship(\'InventoryItem\', backref=\'inventory\', lazy=True, cascade=\'all, delete-orphan\')

    def __repr__(self):
        return f\'<Inventory {self.id}>\'

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey(\'inventory.id\'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey(\'product.id\'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)

    product = db.relationship(\'Product\', backref=db.backref(\'inventory_items\', lazy=True))

    def __repr__(self):
        return f\'<InventoryItem {self.id}>\'
