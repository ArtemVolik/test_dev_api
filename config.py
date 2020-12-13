import os
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'SOMETHING_ABOUT_MARRY'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PAYMENT_METHOD_URLS = {
        'usd': 'https://core.piastrix.com/bill/create',
        'rub': 'https://core.piastrix.com/invoice/create',
        'eur': 'https://pay.piastrix.com/ru/pay'
    }
    SHOP_ID = 5
    PAYMENT_CURRENCIES = [(840, 'USD'), (643, 'RUB'), (978, 'EUR')]
    SHOP_CURRENCY = (643, 'RUB')
    SHOP_SECRET_KEY = os.getenv('SECRET_KEY')