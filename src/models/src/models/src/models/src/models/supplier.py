from ..main import db

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    contact_info = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f\'<Supplier {self.name}>\'
