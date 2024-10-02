from app import app, db  
from app.models import User  
from werkzeug.security import generate_password_hash

def create_admin_account():
   #admin acc details
    admin_username = 'admin'
    admin_email = 'admin@example.com'
    admin_password = 'adminpassword'

  
    existing_user = User.query.filter_by(username=admin_username).first()
    if existing_user:
        print(f"Admin user {admin_username} already exists.")
        return

    # Create a new admin user
    admin_user = User(
        username=admin_username,
        email=admin_email,
        fullname='Administrator',
        role='admin',  
    )
    admin_user.set_password(admin_password)  

    #adding admin to db
    db.session.add(admin_user)
    db.session.commit()
    print(f"Admin account '{admin_username}' created successfully.")


with app.app_context():
    create_admin_account()