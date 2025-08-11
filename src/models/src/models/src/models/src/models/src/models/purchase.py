from ..main import db

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey(\'supplier.id\'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)

    supplier = db.relationship(\'Supplier\', backref=db.backref(\'purchases\', lazy=True))
    items = db.relationship(\'PurchaseItem\', backref=\'purchase\', lazy=True, cascade=\'all, delete-orphan\')

    def __repr__(self):
        return f\'<Purchase {self.id}>\'

class PurchaseItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey(\'purchase.id\'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey(\'product.id\'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)

    product = db.relationship(\'Product\', backref=db.backref(\'purchase_items\', lazy=True))

    def __repr__(self):
        return f\'<PurchaseItem {self.id}>\'
