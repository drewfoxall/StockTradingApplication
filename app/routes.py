from flask import render_template, jsonify, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db  # Import the 'app' instance from __init__.py
from sqlalchemy import text
from app.forms import RegistrationForm, LoginForm, PurchaseForm
from urllib.parse import urlparse
from app.models import user
from flask_wtf import FlaskForm
from app.models import delete_user_by_id, get_all_users,get_user_stocks, user, stock, order, transaction


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        app.logger.info("User is authenticated, redirecting to index.")
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user_obj = user.query.filter_by(user_name=form.username.data).first()  # Query User model
        if user_obj is None or not user_obj.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))  # Redirect back to login if invalid credentials
        
        login_user(user_obj, remember=form.remember_me.data)
        
        # Redirect to next page if available, otherwise redirect to index
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':  # Prevent open redirect attacks
            next_page = url_for('index') 
        return redirect(next_page)
    
    return render_template('login.html', title='Sign In', form=form)
    

@app.route('/portfolio', methods=['GET', 'POST'])
@login_required
def portfolio():
    if current_user.is_authenticated:
        stock = get_user_stocks(current_user.get_id())
        return render_template('portfolio.html', stock=stock)
    else:
        flash('You need to log in to see your portfolio.', 'warning')
        return redirect(url_for('login'))

@app.route('/market')
@login_required
def market():
    stocks = stock.query.all()
    return render_template('market.html')

@app.route('/buy_stock/<int:stock_id>', methods=['GET, POST'])
@login_required
def buy_stock(stock_id):
    form = PurchaseForm()
    stock_to_buy = stock.query.get_or_404(stock_id) #this gets stock according to ID
    quantity = int(request.form['quantity'])
    
   

    if form.validate_on_submit():
        quantity = form.quantity.data

        total_cost = quantity * stock_to_buy.price
        if current_user.cash_balance < total_cost:
            flash('You do not have enough cash in your account to make this transaction', 'danger')
            return redirect(url_for('market'))
        
        new_order = order(
            user_id = current_user.user_id,
            stock_id = stock_id,
            type= 'buy',
            quantity = quantity,
            price = stock_to_buy.price , 
            status = 'pending',
        )
        db.session.add(new_order)

        current_user.cash_balance -= total_cost
        db.session.commit()

        new_transaction = transaction(
            user_id = current_user.user_id,
            stock_id = stock_id,
            type = 'buy',
            quantity = quantity,
            price = stock_to_buy.price
        )
        db.session.add(new_transaction)

        stock_to_buy.volume -= quantity
        db.session.commit()

        existing_portfolio_item = portfolio.query.filter_by(user_id=current_user.user_id, stock_id=stock_id).first()
    if existing_portfolio_item:
        existing_portfolio_item.quantity += quantity  # Update existing quantity
    else:
        new_portfolio_item = portfolio(user_id=current_user.user_id, stock_id=stock_id, quantity=quantity)

    db.session.add(new_portfolio_item)

    # Commit all changes
    db.session.commit()

    flash('Purchase Completed!','Success!')
    return redirect(url_for('portfolio'))
    # return render_template('buy_stock.html', title= 'Buy Stock', form=form, stock = stock_to_buy)


@app.route('/logout')
@login_required
def logout():
    logout_user()  # This logs out the user
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))  # Redirect to the home page after logging out

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
    return render_template('administrator.html', users=users)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('Access denied: Administrator only.', 'danger')
        return redirect(url_for('index'))
    delete_user_by_id(user_id)  # Call delete function from models
    flash(f'User {user_id} has been deleted successfully.', 'success')
    return redirect(url_for('administrator'))


