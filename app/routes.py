from flask import render_template, jsonify, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
#from werkzeug.urls import url_parse
from app import app, db  # Import the 'app' instance from __init__.py
from sqlalchemy import text
from app.forms import RegistrationForm, LoginForm
from app.models import user
from app.models import delete_user_by_id, get_all_users,get_user_stocks


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user_obj = user.query.filter_by(user_name=form.username.data).first()
        if user_obj is None or not user_obj.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user_obj, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page.netloc != '':
            next_page = url_for('index') 
  # Redirect to index if no next page
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/portfolio', methods=['GET', 'POST'])
@login_required
def portfolio():
    if current_user.is_authenticated:
        stock = get_user_stocks(current_user.id)
        return render_template('portfolio.html', stock=stock)
    else:
        flash('You need to log in to see your portfolio.', 'warning')
        return redirect(url_for('login'))

@app.route('/market')
def market():
    return render_template('market.html')
    
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
        new_user = user(user_name=form.user_name.data, email=form.email.data, full_name=form.full_name.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    else:  # Handle GET requests and failed form validation
        return render_template('signup.html', title='Register', form=form)

# Accessing administrator webpage, should be only accessible via logged in Admin page --- not currently working ---
@app.route('/administrator')
@login_required  # Ensure only logged-in users can access this page
def administrator():
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


