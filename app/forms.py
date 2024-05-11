from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError, NumberRange
from .models import User  # Ensure the User model is correctly imported from your integrated models.py

# Register Form
class RegisterForm(FlaskForm):
    def validate_username(self, username_check):
        if User.query.filter_by(username=username_check.data).first():
            raise ValidationError('Username already exists! Please try a different username.')
    
    def validate_email_address(self, email_address_check):
        if User.query.filter_by(email_address=email_address_check.data).first():
            raise ValidationError('Email Address already exists! Please try a different email address.')

    username = StringField(label='User Name', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email Address', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password', validators=[Length(min=3), DataRequired()])
    password2 = PasswordField(label='Confirm Password', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')

# Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

# Purchase Item Form
class PurchaseItemForm(FlaskForm):
    submit = SubmitField(label='Purchase Item!')

# Sell Item Form
class SellItemForm(FlaskForm):
    submit = SubmitField(label='Sell Item!')

class AddItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    barcode = StringField('Barcode', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Add Item')

class SetBudgetForm(FlaskForm):
    budget = IntegerField("Budget", validators=[DataRequired(), NumberRange(min=0)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Set Budget")
