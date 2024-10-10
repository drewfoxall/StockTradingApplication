from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import time
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from app import db, login
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DECIMAL
from decimal import Decimal

bcrypt = Bcrypt()

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
        #hash password with bcrypt
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        #check password with bcrypt
        try:
            is_valid = bcrypt.check_password_hash(self.password_hash, password)
            print(f"Password check for user {self.user_name}: {'Success' if is_valid else 'Failed'}")
            return is_valid
        except Exception as e:
            print(f"Error checking password for user {self.user_name}: {str(e)}")
            return False
    @property
    def is_admin(self):
        return self.role == 'admin'
    def get_id(self):
        return str(self.user_id)

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
    stock_portfolios = db.relationship('portfolio', backref='stock_portfolio_ref', lazy=True)

    def __repr__(self):             # Method useful for debugging and logging
        return f'<stock {self.ticker}: {self.company_name}>'
    
    def update_price(self, new_price):
        """Update price and adjust high/low values"""
        try:
            new_price = Decimal(str(new_price))
            current_date = datetime.now().date()
            
            # Check if we need to reset for a new trading day
            if self.last_updated_date != current_date:
                # Reset high/low for the new day
                self.daily_high = new_price
                self.daily_low = new_price
                self.last_updated_date = current_date
                print(f"New trading day: Reset {self.ticker} high/low to ${new_price}")
            else:
                # Update high/low before changing current price
                if self.daily_high is None or new_price > self.daily_high:
                    self.daily_high = new_price
                    #print(f"New high for {self.ticker}: ${new_price}")
                
                if self.daily_low is None or new_price < self.daily_low:
                    self.daily_low = new_price
                    #print(f"New low for {self.ticker}: ${new_price}")
            
            # Store old price for logging
            old_price = self.price
            
            # Update current price last
            self.price = new_price
            
            # print(
            #     f"Updated {self.ticker} - "
            #     f"Price: ${old_price} -> ${new_price}, "
            #     f"High: ${self.daily_high}, "
            #     f"Low: ${self.daily_low}"
            #)
            
        except Exception as e:
            print(f"Error updating price for {self.ticker}: {str(e)}")
            raise

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
    now = datetime.now()
    current_date = now.strftime('%m-%d')
    
    # Check if today is a holiday
    holiday = Holiday.query.filter_by(date=current_date).first()
    if holiday:
        return False
    
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
    return True

class Holiday(db.Model):
    __tablename__ = 'holiday'
    
    holiday_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(5), nullable=False, unique=True)  # Format: MM-DD
    description = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<Holiday {self.date}: {self.description}>'

@login.user_loader
def load_user(user_id):
    return user.query.get(int(user_id))
