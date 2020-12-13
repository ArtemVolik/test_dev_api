from app import app, db
from app.forms import PaymentForm
from flask import render_template, redirect
from config import Config
from app.models import Payment
import requests


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = PaymentForm()
    if not form.validate_on_submit():
        return render_template('index.html', title='PaymentForm', form=form)
    secret_key = Config.SHOP_SECRET_KEY
    request_urls = Config.PAYMENT_METHOD_URLS
    currencies = [str(i[0]) for i in Config.PAYMENT_CURRENCIES]
    common_params = {
        "shop_id": Config.SHOP_ID,
        "shop_order_id": form.user_shop_order_id.data,
    }
    eur_rub_params = {
        "amount": form.user_amount.data,
        "currency": form.user_currency.data,
    }
    usd_params = {
        "payer_currency": form.user_currency.data,
        "shop_amount": form.user_amount.data,
        "shop_currency": Config.SHOP_CURRENCY[0]
    }
    rub_params = {
        "payway": "payeer_rub",
        "amount": form.user_amount.data,
        "currency": form.user_currency.data
    }
    payment = Payment()
    request_url = False

    if form.user_currency.data == currencies[0]:
        required_params = Payment.make_required_params(common_params, usd_params)
        request_url = request_urls['usd']
    elif form.user_currency.data == currencies[1]:
        required_params = Payment.make_required_params(common_params, rub_params)
        request_url = request_urls['rub']
    elif form.user_currency.data == currencies[2]:
        required_params = Payment.make_required_params(common_params, eur_rub_params)

    params = Payment.make_params(required_params, secret_key)
    payment.payment_save(params, form, db)
    if not request_url:
        url = request_urls['eur']
        return render_template('hidden_form.html', data=params, url=url)
    try:
        response = payment.make_payment_request(params, request_url)
    except requests.exceptions.HTTPError:
        return render_template('index.html', title='Not success', form=form, httperror=True)
    if not response['result']:
        payment.payment_update()
        return render_template('index.html', title='Not success', form=form, response=response)
    payment.payment_update(response)
    response = Payment.response_handling(response)
    if len(response) < 2:
        return redirect(response['url'])
    return render_template('hidden_form.html', data=response['data'], url=response['url'], method=response['method'])

