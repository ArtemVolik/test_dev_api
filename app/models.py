from app import db
from hashlib import sha256
import requests
from datetime import datetime
import dateutil.parser


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.Integer)
    amount = db.Column(db.Float, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    params = db.Column(db.String)
    payment_system_id = db.Column(db.Integer, nullable=True, index=True)
    payment_status = db.Column(db.String, nullable=True, index=True)

    @staticmethod
    def make_required_params(*args) -> dict:
        required_params = {key: value for arg in args for key, value in arg.items()}
        return required_params

    @staticmethod
    def make_sign(required_params, secret_key: str) -> str:
        values_from_params = [str(value) for _, value in sorted(required_params.items())]
        data_for_sign = ':'.join(values_from_params) + secret_key
        sign = sha256(data_for_sign.encode('utf-8')).hexdigest()
        return sign

    @staticmethod
    def make_params(required_params, secret_key: str, **kwargs) -> dict:
        params = required_params
        params['sign'] = Payment.make_sign(required_params, secret_key)
        for item, value in kwargs.items():
            params[item] = value
        return params

    @staticmethod
    def make_payment_request(params, url: str) -> dict:
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=params, headers=headers)
        response.raise_for_status()
        response = response.json()
        return response

    def payment_save(self, params, form):
        self.params = str(params)
        self.amount = form.user_amount.data
        self.currency = form.user_currency.data
        self.payment_status = 'InProcessing'
        db.session.add(self)
        db.session.commit()

    def payment_update(self, response=None):
        if response is None:
            self.payment_status = 'Declined'
        elif response:
            self.payment_system_id = response['data']['id']
            self.timestamp = dateutil.parser.parse(response['data']['created'])
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def response_handling(response):
        url = response['data']['url']
        if 'method' not in response['data']:
            return {'url': url}
        method = response['data']['method']
        data = response['data']['data']
        return {
            'url': url,
            'method': method,
            'data': data
        }


    def get_status(self, response):
        pass

    def __repr__(self):
        return f'<{self.payment_id}>'
