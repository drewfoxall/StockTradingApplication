from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
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