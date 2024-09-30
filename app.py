from flask import Flask, render_template, jsonify
from config import Config
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)
app.config.from_object(Config)

# Database setup
db = SQLAlchemy(app)

if __name__ == '__main__':
    app.run(debug=True)