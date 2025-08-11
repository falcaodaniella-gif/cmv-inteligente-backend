from ..main import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    unit = db.Column(db.String(20), nullable=False) # e.g., Kg, Litro, Unidade
    category = db.Column(db.String(50), nullable=False) # e.g., Hortifruti, Proteína

    def __repr__(self):
        return f\'<Product {self.name}>\'
