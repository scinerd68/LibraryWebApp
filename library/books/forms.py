from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, IntegerField, FieldList, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Length


class InsertBookForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(min=1, max=100)])
    category = StringField("Category", validators=[DataRequired(), Length(min=1, max=100)])
    authors = FieldList(StringField("Author"), min_entries=3, max_entries=3)
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=1, max=500)])
    added_quantity = IntegerField("Number of books to add", validators=[NumberRange(min=0)])
    remove_quantity = IntegerField("Number of books to remove", validators=[NumberRange(min=0)])
    image = FileField('Update Book Cover', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField("Submit")