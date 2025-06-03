from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100))
    amount_paid = db.Column(db.Float)
    payment_date = db.Column(db.Date)
    payment_method = db.Column(db.String(50))
    # Add any other necessary fields...
