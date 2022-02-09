from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DateTimeField, HiddenField, SelectField


class ReturnBookForm(FlaskForm):
    """ Form used to return books """
    book_id = HiddenField()
    user_id = HiddenField()
    title = StringField("Title", render_kw={'readonly': True})
    borrow_date = DateTimeField("Borrow Date", render_kw={'readonly': True}, format="%d/%m/%Y %H:%M")
    return_status = SelectField("Book status", choices=["Normal", "Light Damage", "Heavy Damage", "Lost"])
    late_status = StringField("Late Status", render_kw={'readonly': True})
    damage_fine = IntegerField("Damage Fine", render_kw={'readonly': True})
    late_fine = IntegerField("Late Fine", render_kw={'readonly': True})
    submit = SubmitField("Return")