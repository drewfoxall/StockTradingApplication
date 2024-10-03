from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DECIMAL

class user(UserMixin, db.Model):
 
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(100), nullable=False)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable= False)
    cash_balance = db.Column(db.DECIMAL (10,2), default=0.0)
    role = db.Column(db.String(50), nullable=False, default='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Relationship to orders
    order = db.relationship('order', backref='user')
    transaction = db.relationship('transaction', backref='user')
    portfolio = db.relationship('portfolio', backref='user')

    def get_id(self): 
        return str(self.user_id)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<user {self.user_name}>'

class stock(db.Model):
    """
    Represents stock in the system.
    """
    __tablename__ = 'stock'  # Define the table name

    stock_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_name = db.Column(db.String(100), nullable=False)
    ticker = db.Column(db.String(10), unique=True, nullable=False)
    volume = db.Column(db.Integer, nullable=False)
    price = db.Column(db.DECIMAL(10, 2), nullable=False)

    order = db.relationship('order', backref='stock')
    transaction = db.relationship('transaction', backref='stock')
    portfolio = db.relationship('portfolio', backref='stock')

    def __repr__(self):             # Method useful for debugging and logging
        return f'<stock {self.ticker}: {self.company_name}>'

class market_setting(db.Model):
    """
    Represents market schedule (open, closed, holidays).
    """
    __tablename__ = 'market_setting'  # Define the table name

    market_setting_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    opening_time = db.Column(db.Time, nullable=False)
    closing_time = db.Column(db.Time, nullable=False)
    trading_days = db.Column(db.String(50), nullable=False)  # You may want to adjust the type based on your needs
    holidays = db.Column(db.String(255), nullable=True)  # Can store holidays as a string (comma-separated, JSON, etc.)

    def __repr__(self):
        return f'<market_setting {self.market_setting_id}: {self.opening_time} - {self.closing_time}>'

class order(db.Model):
    """
    Represents a customer-initiated transaction (one or many).
    """
    __tablename__ = 'order'  # Define the table name

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)  # Foreign key to user table
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.stock_id'), nullable=False)  # Foreign key to stocks table
    type = db.Column(db.String(10), nullable=False)  # e.g., 'buy' or 'sell'
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.DECIMAL(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # e.g., 'pending', 'completed', 'canceled'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<order {self.order_id}: {self.type} {self.quantity} of stock {self.stock_id} by user {self.user_id}>'

class transaction(db.Model):
    """
    Represents all transactions in the system.
    """
    __tablename__ = 'transaction'  # Define the table name

    transaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)  # Assuming there's a users table
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.stock_id'), nullable=False)  # Assuming there's a stocks table
    type = db.Column(db.String(10), nullable=False)  # e.g., 'buy' or 'sell'
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.DECIMAL(10, 2), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<transaction {self.transaction_id}: {self.type} {self.quantity} of stock {self.stock_id} by User {self.user_id}>'

class portfolio(db.Model):
    """
    Represents one or many stock owned by the customer.
    """
    __tablename__ = 'portfolio'  # Define the table name

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))  # No longer primary key here
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.stock_id'), nullable=False)  # Foreign key
    quantity = db.Column(db.Integer, nullable=False)
    
    __table_args__ = (db.PrimaryKeyConstraint('user_id', 'stock_id'),)  # Composite primary key

    def __repr__(self):
        return f'<portfolio user {self.user_id}: stock {self.stock_id} - quantity {self.quantity}>'

#################################################################################################
#################################################################################################


    # Relationships (add these as implement other features)
    # transactions = db.relationship('Transaction', backref='user', lazy=True)
    # portfolio = db.relationship('portfolio', backref='user', lazy=True)
    # orders = db.relationship('order', backref='user', lazy=True) 
    # Flask-Login integration

def delete_user_by_id(user_id):
    user = user.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

def get_all_users():
    users = user.query.all()
    return users

def get_user_stocks(user_id):
    """
    Retrieves the stocks owned by a specific user.
    """
    # This query joins the portfolio and stock tables to get the stock details for a user
    query = db.session.query(stock, portfolio.quantity).join(portfolio).filter(portfolio.user_id == user_id)
    return query.all()

@login.user_loader
def load_user(user_id):
    return user.query.get(int(user_id))
