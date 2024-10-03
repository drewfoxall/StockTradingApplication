from flask import render_template, jsonify, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db  # Import the 'app' instance from __init__.py
from sqlalchemy import text
from app.forms import RegistrationForm
from app.models import User
from app.models import delete_user_by_id, get_all_users,get_user_stocks


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
@login_required
def portfolio():
    if current_user.is_authenticated:
        stocks = get_user_stocks(current_user.id)
        return render_template('portfolio.html', stocks=stocks)
    else:
        flash('You need to log in to see your portfolio.', 'warning')
        return redirect(url_for('login'))
    

@app.route('/test_db')
def test_db():
    try:
        # Attempt a simple query to check the connection
        db.session.execute(text('SELECT 1')) 
        return jsonify({'status': 'success', 'message': 'Database connection successful!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Database connection failed: {str(e)}'})

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit(): 
        user = User(user_name=form.username.data, email=form.email.data, full_name=form.fullname.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    else:  # Handle GET requests and failed form validation
        return render_template('signup.html', title='Register', form=form)
    return render_template('signup.html', title='Register', form=form)

# Accessing administrator webpage, should be only accessible via logged in Admin page --- not currently working ---
@app.route('/administrator')
@login_required  # Ensure only logged-in users can access this page
def admin_page():
    if not current_user.is_admin:  
        flash('Access denied: Administrator only.', 'danger')
        return redirect(url_for('index'))
    users = get_all_users()  
    return render_template('admin.html', users=users)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('Access denied: Administrator only.', 'danger')
        return redirect(url_for('index'))
    delete_user_by_id(user_id)  # Call delete function from models
    flash(f'User {user_id} has been deleted successfully.', 'success')
    return redirect(url_for('admin_page'))


