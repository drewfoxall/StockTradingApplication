from flask_login import UserMixin
from datetime import time
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from app import db, login
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DECIMAL

# List of major holidays (MM-DD format)
holidays = [
    '01-01',  # New Year's Day
    '07-04',  # Independence Day
    '12-25',  # Christmas Day
    # Add more holidays here
]
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
        print(f"Password from form: {password}")
        print(f"Stored password hash: {self.password_hash}")
        result = check_password_hash(self.password_hash, password)
        print(f"Password check result: {result}")
        return result
    @property
    def is_admin(self):
        return self.role == 'admin'

# Relationship to orders
    order = db.relationship('order', backref='user')
    transaction = db.relationship('transaction', backref='user')
    portfolio = db.relationship('portfolio', backref='user')

    def get_id(self): 
        return str(self.user_id)

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
    original_price = db.Column(db.DECIMAL(10, 2), nullable=False)
    daily_high = db.Column(db.DECIMAL(10, 2), nullable=True)
    daily_low = db.Column(db.DECIMAL(10, 2), nullable=True)
    last_updated_date = db.Column(db.Date, nullable=True)

    stock_orders = db.relationship('order', backref='stock_order_ref')
    #stock_transactions = db.relationship('transaction', backref='stock_transaction_ref')
    stock_portfolios = db.relationship('portfolio', backref='stock_portfolio_ref', lazy=True)

    def __repr__(self):             # Method useful for debugging and logging
        return f'<stock {self.ticker}: {self.company_name}>'

class market_setting(db.Model):
    """
    Represents market schedule (open, closed, holidays).
    """
    __tablename__ = 'market_setting'  # Define the table name

    market_setting_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    is_market_open = db.Column(db.Boolean, default=False)
    opening_time = db.Column(db.Time, nullable=False, default=time(9, 0))
    closing_time = db.Column(db.Time, nullable=False, default=time(16, 0))
    trading_days = db.Column(db.String(50), nullable=False, default='1,2,3,4,5')  # You may want to adjust the type based on your needs
    holidays = db.Column(db.Text, nullable=True)  # Can store holidays as a string (comma-separated, JSON, etc.)

    def __init__(self):
        self.is_market_open = False
        self.opening_time = time(9, 0)
        self.closing_time = time(16, 0)
        self.trading_days = '1,2,3,4,5'
        self.holidays = '[]'  # Empty JSON array as string

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
    time_stamp = db.Column(db.DateTime, default=datetime.utcnow)

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
    time_stamp = db.Column(db.DateTime, default=datetime.utcnow)
    stock = db.relationship('stock', backref='transaction_ref', lazy=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.stock_id'), nullable=False)


    def __repr__(self):
        return f'<transaction {self.transaction_id}: {self.type} {self.quantity} of stock {self.stock_id} by User {self.user_id}>'

class portfolio(db.Model):
    """
    Represents one or many stock owned by the customer.
    """
    __tablename__ = 'portfolio'  # Define the table name

    portfolio_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)  # No longer primary key here
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.stock_id'), nullable=False)  # Foreign key
    quantity = db.Column(db.Integer, nullable=False)
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
    user_todelete = user.query.get(user_id)  # Ensure 'user' is the correct model name
    if user_todelete:
        db.session.delete(user_todelete)
        db.session.commit()
        return True
    return False

def get_all_users():
    users = user.query.all()
    return users

# def get_user_stocks(user_id):
#     """
#     Retrieves the stocks owned by a specific user.
#     """
#     # This query joins the portfolio and stock tables to get the stock details for a user
#     query = db.session.query(stock, portfolio.quantity).join(portfolio).filter(portfolio.user_id == user_id)
#     user_stocks = query.all()  # Execute the query and get the results

#     # Create a list of dictionaries to store the stock information
#     stock_list = []
#     for stock_obj, quantity in user_stocks:
#         stock_info = {
#             'ticker': stock_obj.ticker,
#             'company_name': stock_obj.company_name,
#             'quantity': quantity,
#             'price': stock_obj.price
#         }
#         stock_list.append(stock_info)

#     return stock_list  # Return the list of dictionaries

def get_user_stocks(user_id):
    """
    Retrieves the stocks owned by a specific user.
    """
    user_stocks = []
    portfolio_entries = portfolio.query.filter_by(user_id=user_id).all()
    for entry in portfolio_entries:
        stock_data = stock.query.get(entry.stock_id)
        if stock_data:
            user_stocks.append(stock_data)  # Append the Stock object directly
        else:
            print(f"Warning: Stock not found for stock_id: {entry.stock_id}")
    return user_stocks

def is_market_open():
    """Check if the market is currently open"""
    
    setting = market_setting.query.first()
    if not setting:
        return False

    now = datetime.now()
    current_time = now.time()

    # More robust time comparison
    if setting.opening_time < setting.closing_time:
        is_open = setting.opening_time <= current_time <= setting.closing_time
    else:  # Handle cases where closing time is after midnight
        is_open = current_time >= setting.opening_time or current_time <= setting.closing_time

    if not is_open:
        return False

    # Check if today is a trading day (Monday is 0, Sunday is 6)
    today = datetime.now().weekday()
    if not setting.trading_days:  # Check if trading_days is empty or None
        return False  # Or handle it differently, e.g., set a default
    trading_days = list(map(int, setting.trading_days.split(',')))  # Convert to list of integers
    if today + 1 not in trading_days:  # Adjust today's index to match your format (1-7)
        return False
       # Check if today is a holiday
    today_date = datetime.now().strftime('%m-%d')
    if today_date in holidays:
        return False

    return True

@login.user_loader
def load_user(user_id):
    return user.query.get(int(user_id))
