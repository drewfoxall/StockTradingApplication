import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '50UEzfDVvZWCGhBEf2AFOYxnlfYNUNgq7JFBxEmL'  # Replace with a strong secret key
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://admin:SunDevils24!@stocktrader-database-1.cpskyc0uqfeb.us-west-2.rds.amazonaws.com:3306/stock_trader_database'
    SQLALCHEMY_TRACK_MODIFICATIONS = False