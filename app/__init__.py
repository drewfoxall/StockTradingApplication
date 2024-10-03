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


# Import routes
from app import routes, models