from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, HiddenField, SubmitField


class ReleaseItemsForm(FlaskForm):
    items_name = TextField("items_name")
    price = TextField("price")
    desc = TextAreaField("desc")
    main_picture_url = TextField("main_picture_url")
    submit = SubmitField("Submit")

