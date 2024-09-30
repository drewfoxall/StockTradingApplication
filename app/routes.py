from flask import render_template, jsonify
from app import app, db  # Import the 'app' instance from __init__.py
from sqlalchemy import text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/administrator')
def administrator():
    return render_template('administrator.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/market')
def market():
    return render_template('market.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/test_db')
def test_db():
    try:
        # Attempt a simple query to check the connection
        db.session.execute(text('SELECT 1')) 
        return jsonify({'status': 'success', 'message': 'Database connection successful!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Database connection failed: {str(e)}'})

