from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, TextAreaField, FloatField
from wtforms.validators import DataRequired, Length, ValidationError
from config import Config


class MyFloatField(FloatField):
    def process_formdata(self, value):
        if not value:
            return
        try:
            self.data = float(value[0].replace(',', '.'))
        except ValueError:
            self.data = None
            raise ValueError(self.gettext('Не корректный формат суммы'))


class PaymentForm(FlaskForm):
    user_amount = MyFloatField(
        u'Сумма оплаты', validators=[DataRequired(message=u'Введите сумму')])
    user_currency = SelectField(
        u'Валюта оплаты', choices=Config.PAYMENT_CURRENCIES,
        validators=[DataRequired()])
    user_shop_order_id = TextAreaField(
        u'Описание товара', validators=[Length(
            min=1, max=255, message=u'Поле не должно быть пустым, и должно быть не больше 255 знаков')])
    submit = SubmitField(u'Оплатить')

    def validate_user_amount(self, user_amount):
        value = str(user_amount.data)
        if not '.' in value:
            return
        value = value.split('.')
        if len(value[1]) > 2:
            raise ValidationError('Сумма должна содержать 2 знака после разделителя')

