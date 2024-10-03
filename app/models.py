from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login
from flask_sqlalchemy import SQLAlchemy

class User(UserMixin, db.Model):
    """
    Represents a user in the system (customer or admin).
    """
#   id = db.Column(db.Integer, primary_key=True)
#   username = db.Column(db.String(64), index=True, unique=True, nullable=False)
#    password_hash = db.Column(db.String(128))  # Store hashed passwords
#    fullname = db.Column(db.String(128), nullable=False)
#    email = db.Column(db.String(128), unique=True, nullable=False)
#    role = db.Column(db.String(10), nullable=False, default='customer')  # Default to 'customer'
#    cash_balance = db.Column(db.DECIMAL(10, 2), nullable=False, default=0)

    __tablename__ = 'user'

    UserID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FullName = db.Column(db.String(100), nullable=False)
    Username = db.Column(db.String(50), unique=True, nullable=False)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    PasswordHash = db.Column(db.String(128), nullable=False)
    CashBalance = db.Column(db.Float, default=0.0)
    Role = db.Column(db.String(50), nullable=False)

# Relationship to orders
    order = db.relationship('Order', backref='user')

def __repr__(self):
    return f'<User {self.Username}>'

class Stocks(db.Model):
    """
    Represents stocks in the system.
    """
    __tablename__ = 'stocks'  # Define the table name

    StockID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    CompanyName = db.Column(db.String(100), nullable=False)
    Ticker = db.Column(db.String(10), unique=True, nullable=False)
    Volume = db.Column(db.Integer, nullable=False)
    Price = db.Column(db.Float, nullable=False)

def __repr__(self):             # Method useful for debugging and logging
    return f'<Stock {self.Ticker}: {self.CompanyName}>'

class MarketSettings(db.Model):
    """
    Represents market schedule (open, closed, holidays).
    """
    __tablename__ = 'market_settings'  # Define the table name

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    OpeningTime = db.Column(db.Time, nullable=False)
    ClosingTime = db.Column(db.Time, nullable=False)
    TradingDays = db.Column(db.String(50), nullable=False)  # You may want to adjust the type based on your needs
    Holidays = db.Column(db.String(255), nullable=True)  # Can store holidays as a string (comma-separated, JSON, etc.)

def __repr__(self):
    return f'<MarketSettings {self.ID}: {self.OpeningTime} - {self.ClosingTime}>'

class Order(db.Model):
    """
    Represents a customer-initiated transaction (one or many).
    """
    __tablename__ = 'order'  # Define the table name

    OrderID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey('user.UserID'), nullable=False)  # Foreign key to user table
    StockID = db.Column(db.Integer, db.ForeignKey('stocks.StockID'), nullable=False)  # Foreign key to stocks table
    Type = db.Column(db.String(10), nullable=False)  # e.g., 'buy' or 'sell'
    Quantity = db.Column(db.Integer, nullable=False)
    Price = db.Column(db.Float, nullable=False)
    Status = db.Column(db.String(20), nullable=False)  # e.g., 'pending', 'completed', 'canceled'
    Timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Relationships
user = db.relationship('User', backref='order')
stocks = db.relationship('Stocks', backref='order')

def __repr__(self):
    return f'<Order {self.OrderID}: {self.Type} {self.Quantity} of Stocks {self.StockID} by User {self.UserID}>'

class Transaction(db.Model):
    """
    Represents all transactions in the system.
    """
    __tablename__ = 'transaction'  # Define the table name

    TransactionID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey('user.UserID'), nullable=False)  # Assuming there's a users table
    StockID = db.Column(db.Integer, db.ForeignKey('stocks.StockID'), nullable=False)  # Assuming there's a stocks table
    Type = db.Column(db.String(10), nullable=False)  # e.g., 'buy' or 'sell'
    Quantity = db.Column(db.Integer, nullable=False)
    Price = db.Column(db.Float, nullable=False)
    Timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Optional: Relationships
user = db.relationship('User', backref='transaction')
stocks = db.relationship('Stocks', backref='transaction')

def __repr__(self):
    return f'<Transaction {self.TransactionID}: {self.Type} {self.Quantity} of Stocks {self.StockID} by User {self.UserID}>'

class Portfolio(db.Model):
    """
    Represents one or many stocks owned by the customer.
    """
    __tablename__ = 'portfolio'  # Define the table name

    UserID = db.Column(db.Integer, nullable=False)  # No longer primary key here
    StockID = db.Column(db.Integer, db.ForeignKey('stocks.StockID'), nullable=False)  # Foreign key
    Quantity = db.Column(db.Integer, nullable=False)

    __table_args__ = (db.PrimaryKeyConstraint('UserID', 'StockID'),)  # Composite primary key

# Optional: Relationships
user = db.relationship('User', backref='portfolio')
stock = db.relationship('Stocks', backref='portfolio')

def __repr__(self):
    return f'<Portfolio User {self.UserID}: Stocks {self.StockID} - Quantity {self.Quantity}>'

#################################################################################################
#################################################################################################


    # Relationships (you'll add these as you implement other features)
    # transactions = db.relationship('Transaction', backref='user', lazy=True)
    # portfolios = db.relationship('Portfolio', backref='user', lazy=True)
    # orders = db.relationship('Order', backref='user', lazy=True) 

    def set_password(self, password):
        self.PasswordHash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.PasswordHash, password)

    # Flask-Login integration
    def get_id(self): 
        return str(self.UserID)  

@login.user_loader
def load_user(id):
    return User.query.get(int(id))