from tkinter.tix import Select
from tokenize import Number
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField,\
    IntegerField, FieldList, TextAreaField, DateTimeField, HiddenField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from library.models import User


class RegistrationForm(FlaskForm):
    username = StringField("Username",
                          validators=[DataRequired(), Length(min=2, max=20)])
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
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
    title = StringField("Title", validators=[DataRequired()])
    category = StringField("Category", validators=[DataRequired()])
    authors = FieldList(StringField("Author"), min_entries=3, max_entries=3)
    description = TextAreaField('Description', validators=[DataRequired()])
    added_quantity = IntegerField("Number of books to add", validators=[NumberRange(min=0)])
    remove_quantity = IntegerField("Number of books to remove", validators=[NumberRange(min=0)])
    image = FileField('Update Book Cover', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField("Submit")


class ReturnBookForm(FlaskForm):
    book_id = HiddenField()
    user_id = HiddenField()
    title = StringField("Title", render_kw={'readonly': True})
    borrow_date = DateTimeField("Borrow Date", render_kw={'readonly': True}, format="%d/%m/%Y %H:%M")
    return_status = SelectField("Book status", choices=["Normal", "Light Damage", "Heavy Damage", "Lost"])
    late_status = StringField("Late Status", render_kw={'readonly': True})
    damage_fine = IntegerField("Damage Fine", render_kw={'readonly': True})
    late_fine = IntegerField("Late Fine", render_kw={'readonly': True})
    submit = SubmitField("Return")
