import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env')) 

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://admin:SunDevils24!@stocktrader-database-1.cpskyc0uqfeb.us-west-2.rds.amazonaws.com:3306/stock_trader_database'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Set "Remember Me" cookie duration (e.g., 30 days)
    REMEMBER_COOKIE_DURATION = timedelta(days=10)