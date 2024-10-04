from flask import render_template, jsonify, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db  # Import the 'app' instance from __init__.py
from sqlalchemy import text
from app.forms import RegistrationForm, LoginForm, PurchaseForm, AdminCreationForm
from urllib.parse import urlparse
from app.models import user, delete_user_by_id, get_all_users, get_user_stocks, stock, order, transaction, market_setting
from flask_wtf import FlaskForm
from decimal import Decimal


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
        #next_page = request.args.get('next')
        #if not next_page or urlparse(next_page).netloc != '':  # Prevent open redirect attacks
            #next_page = url_for('portfolio') 
        #return redirect(next_page)
        # Redirect based on user role
        if user_obj.is_admin:
            return redirect(url_for('administrator'))  # Redirect to admin page
        else:
            return redirect(url_for('portfolio'))  # Redirect to portfolio page
    return render_template('login.html', title='Sign In', form=form)
    
@app.route('/portfolio', methods=['GET', 'POST'])
@login_required
def portfolio():
    if current_user.is_authenticated:
        user_stocks = get_user_stocks(current_user.get_id())
        all_stocks = stock.query.all()
        return render_template('portfolio.html', stock=user_stocks, stocks=all_stocks)
    else:
        flash('You need to log in to see your portfolio.', 'warning')
        return redirect(url_for('login'))

@app.route('/market')
@login_required
def market():
    stocks = stock.query.all()
    return render_template('market.html')

@app.route('/update_market_hours', methods=['POST'])
@login_required
def update_market_hours():
    if not current_user.is_admin:
        flash('You do not have permission to update market hours.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Get the opening and closing times from the form
        opening_time = request.form.get('opening_time')
        closing_time = request.form.get('closing_time')

        # Validate the input (ensure they are valid times, etc.)

        # Update the market settings in the database
        market_setting = market_setting.query.get(1)  # Assuming you have only one market setting
        if market_setting:
            market_setting.opening_time = opening_time
            market_setting.closing_time = closing_time
            db.session.commit()
            flash('Market hours updated successfully!', 'success')
        else:
            flash('Market settings not found.', 'danger')

    return redirect(url_for('administrator'))

@app.route('/add_update_stock', methods=['POST'])
@login_required
def add_update_stock():
    if not current_user.is_admin:
        flash('You do not have permission to add or update stocks.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Get the stock data from the form
        ticker = request.form.get('ticker')
        company_name = request.form.get('company_name')
        price = request.form.get('price')
        volume = request.form.get('volume')

        # Validate the input (ensure they are valid values, etc.)

        # Check if the stock already exists
        existing_stock = stock.query.filter_by(ticker=ticker).first()
        if existing_stock:
            # Update the existing stock
            existing_stock.company_name = company_name
            existing_stock.price = price
            existing_stock.volume = volume
            flash('Stock updated successfully!', 'success')
        else:
            # Create a new stock
            new_stock = stock(
                ticker=ticker,
                company_name=company_name,
                price=price,
                volume=volume
            )
            db.session.add(new_stock)
            flash('Stock added successfully!', 'success')

        db.session.commit()

    return redirect(url_for('administrator'))

@app.route('/buy_stock/<int:stock_id>', methods=['GET, POST'])
@login_required
def buy_stock(stock_id):
    form = PurchaseForm()
    stock_to_buy = stock.query.get_or_404(stock_id) #this gets stock according to ID
    #quantity = int(request.form['quantity'])
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

@app.route('/delete_stock/<int:stock_id>', methods=['POST'])
@login_required
def delete_stock(stock_id):
    if not current_user.is_admin:
        flash('You do not have permission to delete stocks.', 'danger')
        return redirect(url_for('index'))

    stock_to_delete = stock.query.get_or_404(stock_id)
    try:
        db.session.delete(stock_to_delete)
        db.session.commit()
        flash('Stock deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting stock: {e}', 'danger')

    return redirect(url_for('administrator'))

@app.route('/deposit_cash', methods=['POST'])
@login_required
def deposit_cash():
    if request.method == 'POST':
        amount = Decimal(request.form['amount'])
        current_user.cash_balance += amount
        db.session.commit()
        flash('Cash deposited successfully!', 'success')
    return redirect(url_for('portfolio'))

@app.route('/withdraw_cash', methods=['POST'])
@login_required
def withdraw_cash():
    if request.method == 'POST':
        amount = Decimal(request.form['amount'])
        current_user.cash_balance -= amount
        db.session.commit()
        flash('Cash withdrawn successfully!', 'success')
    return redirect(url_for('portfolio'))

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
    stocks = stock.query.all()
    market_settings = market_setting.query.first()
    if not market_settings:
        market_settings = market_setting()
        db.session.add(market_settings)
        db.session.commit()
    return render_template(
        'administrator.html',
        users=users,
        stocks=stocks,
        market_settings=market_settings  # Pass market_settings to the template
    )

@app.route('/create_admin', methods=['GET', 'POST'])
@login_required
def create_admin():
    if not current_user.is_admin:
        flash('You do not have permission to create an admin account.', 'danger')
        return redirect(url_for('index'))

    form = AdminCreationForm()
    if form.validate_on_submit():
        new_admin = user(
            user_name=form.username.data,
            email=form.email.data,
            role='admin'  # Set the role to 'admin'
        )
        new_admin.set_password(form.password.data)
        db.session.add(new_admin)
        db.session.commit()
        flash('Admin account created successfully!', 'success')
        return redirect(url_for('administrator'))
    return render_template('create_admin.html', form=form)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('Access denied: Administrator only.', 'danger')
        return redirect(url_for('index'))
    delete_user_by_id(user_id)  # Call delete function from models
    flash(f'User {user_id} has been deleted successfully.', 'success')
    return redirect(url_for('administrator'))


