from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from library.models import User


class RegistrationForm(FlaskForm):
    username = StringField("Username",
                          validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email",
                       validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", 
                                    validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()

        if user is not None:
            raise ValidationError("Username is taken. Please change username.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user is not None:
            raise ValidationError("Email is taken. Please choose a different email.")


class LoginForm(FlaskForm):
    email = StringField("Email",
                       validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField("Log in")
    librarian = BooleanField('I am librarian.')


class InsertBookForm(FlaskForm):
    title = StringField("Title")
    category = StringField("Category")
    author = StringField("Author")
    added_quantity = IntegerField("Number of books to add")
    submit = SubmitField("Add")
