from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import TextField, TextAreaField, HiddenField, SubmitField, DecimalField, FileField
from wtforms.validators import Email, NumberRange, InputRequired, ValidationError


class ReleaseItemsForm(FlaskForm):
    items_name = TextField("items_name", validators=[InputRequired(message="请输入商品名称")])
    price = DecimalField("price", validators=[NumberRange(min=0, message="请输入正确的价格（只能包含数字且大于等于0）")])
    desc = TextAreaField("desc")
    main_picture_url = TextField("main_picture_url")
    main_picture = FileField(validators=[FileAllowed(['jpg', 'png', 'webp', 'jpeg'], '仅支持上传 jpg, png, webp, jpeg')])
    submit = SubmitField("Submit")


class PurchaseItemsForm(FlaskForm):
    email = TextField("email", validators=[Email(message='Email格式输入错误')])
    phone = TextField("phone", validators=[InputRequired(message="请输入手机号")])
    location = TextField("location")
    comment = TextAreaField("comment")
    submit = SubmitField("Submit")


def is_float(data):
    try:
        float(data)
    except:
        return False
    return True

def numberRange_or_null_check(form, field):
    data:str = field.data
    min = 0
    if (data != "" and not is_float(data)) or (data != "" and data is not None and float(data) < min):
        raise ValidationError("请输入正确的价格（只能包含数字且大于等于0）")






class ChangeItemsForm(FlaskForm):
    items_name = TextField("items_name")
    price = TextField("price", validators=[numberRange_or_null_check])
    desc = TextAreaField("desc")
    main_picture_url = TextField("main_picture_url")
    main_picture = FileField(validators=[FileAllowed(['jpg', 'png', 'webp', 'jpeg'], '仅支持上传 jpg, png, webp, jpeg')])
    submit = SubmitField("Submit")
