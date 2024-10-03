from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DECIMAL


class User(UserMixin, db.Model):
 

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
    orders = db.relationship('order', backref='user')

def __repr__(self):
    return f'<User {self.Username}>'

class Stock(db.Model):
    """
    Represents stock in the system.
    """
    __tablename__ = 'stocks'  # Define the table name

    stock = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_name = db.Column(db.String(100), nullable=False)
    ticker = db.Column(db.String(10), unique=True, nullable=False)
    volume = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

def __repr__(self):             # Method useful for debugging and logging
    return f'<Stock {self.ticker}: {self.CompanyName}>'

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
    return f'<market_setting {self.ID}: {self.opening_time} - {self.closing_time}>'

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
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # e.g., 'pending', 'completed', 'canceled'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Relationships
user = db.relationship('User', backref='order')
stock = db.relationship('stock', backref='order')

def __repr__(self):
    return f'<order {self.order_id}: {self.Type} {self.quantity} of Stocks {self.stock_id} by User {self.user_id}>'

class transaction(db.Model):
    """
    Represents all transactions in the system.
    """
    __tablename__ = 'transaction'  # Define the table name

    transaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)  # Assuming there's a users table
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)  # Assuming there's a stocks table
    type = db.Column(db.String(10), nullable=False)  # e.g., 'buy' or 'sell'
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    time_stamp = db.Column(db.DateTime, default=datetime.utcnow)

# Optional: Relationships
user = db.relationship('user', backref='transaction')
stock = db.relationship('stock', backref='transaction')

def __repr__(self):
    return f'<Transaction {self.transaction_id}: {self.type} {self.quantity} of Stocks {self.stock_id} by User {self.user_id}>'

class portfolio(db.Model):
    """
    Represents one or many stocks owned by the customer.
    """
    __tablename__ = 'portfolio'  # Define the table name

    user_id = db.Column(db.Integer, nullable=False)  # No longer primary key here
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.StockID'), nullable=False)  # Foreign key
    Quaquantityntity = db.Column(db.Integer, nullable=False)

    __table_args__ = (db.PrimaryKeyConstraint('user_id', 'stock_id'),)  # Composite primary key

# Optional: Relationships
user = db.relationship('user', backref='portfolio')
stock = db.relationship('stock', backref='portfolio')

def __repr__(self):
    return f'<portfolio user {self.user_id}: Stocks {self.stock_id} - Quantity {self.quantity}>'

#################################################################################################
#################################################################################################


    # Relationships (you'll add these as you implement other features)
    # transactions = db.relationship('Transaction', backref='user', lazy=True)
    # portfolios = db.relationship('Portfolio', backref='user', lazy=True)
    # orders = db.relationship('Order', backref='user', lazy=True) 


    # Flask-Login integration
def get_id(self): 
    return str(self.user_id)

@property
def is_admin(self):
    return self.role == 'admin'

def delete_user_by_id(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

def get_all_users():
    users = User.query.all()
    return users

def get_user_stocks(user_id):
    """
    Retrieves the stocks owned by a specific user.
    """
    # This query joins the Portfolios and Stocks tables to get the stock details for a user
    query = db.session.query(stock, portfolio.quantity).join(portfolio).filter(portfolio.user_id == user_id)
    return query.all()

@login.user_loader
def load_user(user_id):
    return user_id.query.get(int(id))