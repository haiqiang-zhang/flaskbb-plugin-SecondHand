from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, HiddenField, SubmitField, DecimalField
from wtforms.validators import Email, NumberRange, InputRequired


class ReleaseItemsForm(FlaskForm):
    items_name = TextField("items_name", validators=[InputRequired(message="请输入商品名称")])
    price = DecimalField("price", validators=[NumberRange(min=0, message="请输入正确的价格（只能包含数字）")])
    desc = TextAreaField("desc")
    main_picture_url = TextField("main_picture_url")
    submit = SubmitField("Submit")

class PurchaseItemsForm(FlaskForm):
    email = TextField("email", validators=[Email(message='Email格式输入错误')])
    phone = TextField("phone")
    location = TextField("location")
    comment = TextAreaField("comment")
    submit = SubmitField("Submit")



