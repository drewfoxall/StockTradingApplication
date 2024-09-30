from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)

# Database setup
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Login manager setup
login = LoginManager(app)
login.login_view = 'login' 

# User loader function for Flask-Login
@login.user_loader
def load_user(user_id):
    from app.models import User  # Import User model here to avoid circular imports
    return User.query.get(int(user_id))

# Import routes
from app import routes