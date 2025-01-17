from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, DataRequired, Regexp, Length
from app import db
from app.models import user as UserModel

class RegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    user_name = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, user_name):
        user_obj = UserModel.query.filter_by(user_name=user_name.data).first()
        if user_obj is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user_obj = UserModel.query.filter_by(email=email.data).first()
        if user_obj is not None:
            raise ValidationError('Please use a different email address.')
        
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

# class PurchaseForm(FlaskForm):
#     quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])

class AdminCreationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Create Admin')
    is_admin = BooleanField('Admin')
    submit = SubmitField('Create User')  # Changed button label

class HolidayForm(FlaskForm):
    date = StringField('Date (MM-DD)', 
                      validators=[
                          DataRequired(),
                          Regexp(r'^(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$', 
                                message='Date must be in MM-DD format')
                      ])
    description = StringField('Description', 
                            validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Add Holiday')