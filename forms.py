"""Forms for SaferSexNYC app"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, IntegerField
from wtforms.validators import InputRequired, Length, Email

class RegisterForm(FlaskForm):
    """Form for new user registration"""

    first_name = StringField("First Name", validators=[InputRequired(), Length(max=40, message="First Name cannot exceed 40 characters.")])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(max=40, message="Last Name cannot exceed 40 characters.")])
    email = StringField("Email Address", validators=[InputRequired(), Email()])
    zip_code = StringField("Zip Code (optional)", validators=[Length(min=5, max=5)], description="optional")
    username = StringField("Username", validators=[InputRequired(), Length(max=30, message="Username cannot exceed 30 characters.")])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, message="Password must be at least 8 characters.")])

class LoginForm(FlaskForm):
    """Form for existing users to verify login credentials in order to access private content"""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class UpdateUserForm(FlaskForm):
    """Form for updating user information"""

    first_name = StringField("First Name", validators=[InputRequired(), Length(max=40, message="First Name cannot exceed 40 characters.")])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(max=40, message="Last Name cannot exceed 40 characters.")])
    email = StringField("Email Address", validators=[InputRequired(), Email()])
    zip_code = StringField("Zip Code", validators=[Length(min=5, max=5)])
    username = StringField("Username", validators=[InputRequired(), Length(max=30, message="Username cannot exceed 30 characters.")])

class CommentForm(FlaskForm):
    """Form for creating or updating a comment"""

    content = TextAreaField("Comment", validators=[InputRequired()])
    private = BooleanField("Private Comment")

