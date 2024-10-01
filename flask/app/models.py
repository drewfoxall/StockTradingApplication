from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login

class User(UserMixin, db.Model):
    """
    Represents a user in the system (customer or admin).
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))  # Store hashed passwords
    fullname = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    role = db.Column(db.String(10), nullable=False, default='customer')  # Default to 'customer'
    cash_balance = db.Column(db.DECIMAL(10, 2), nullable=False, default=0)

    # Relationships (you'll add these as you implement other features)
    # transactions = db.relationship('Transaction', backref='user', lazy=True)
    # portfolios = db.relationship('Portfolio', backref='user', lazy=True)
    # orders = db.relationship('Order', backref='user', lazy=True) 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Flask-Login integration
    def get_id(self): 
        return str(self.id)  

@login.user_loader
def load_user(id):
    return User.query.get(int(id))