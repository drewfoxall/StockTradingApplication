from flask import Flask
from flask_bcrypt import Bcrypt
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from threading import Thread

# Create the Flask application
app = Flask(__name__)
app.config.from_object(Config)
bcrypt = Bcrypt(app)

# Database setup
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Login manager setup
login = LoginManager(app)
login.login_view = 'login'

# Import routes after app initialization to avoid circular imports
from app import routes, models

# Start the price adjuster if not in debug mode
if not app.debug:
    price_thread = Thread(target=routes.adjust_prices, daemon=True)
    price_thread.start()