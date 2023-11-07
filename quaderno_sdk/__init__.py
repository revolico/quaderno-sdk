#!/usr/bin/env python

__version__ = '0.0.5'

import json
import requests


class QuadernoError(Exception):

    """
    Quaderno.io exception handling
    """

    def __init__(self, response: requests.Response = None):
        self.response = response
        self.code = response.status_code
        self.errors = None

        if response is not None:
            try:
                error = json.loads(response.content)
            except ValueError:
                self.message = 'Unknown Error'
            else:
                if 'errors' in error:
                    self.message = 'Validation Error'
                    self.errors = error['errors']
                else:
                    self.message = error.get('error', 'HTTP Error')

    def get_reatelimit(self):
        """
        https://github.com/quaderno/quaderno-api#rate-limiting
        """
        headers = self.response.headers

        return {
            'remaining': headers.get('x-ratelimit-remaining'),
            'reset': headers.get('x-ratelimit-reset')
        }

    def __str__(self):
        return f'{self.code}.{self.message}'

    def __repr__(self):
        return str(self)


class Client(object):

    """
    A client for the Quaderno.io REST API.
    See https://quaderno.io/docs/ and
    https://github.com/quaderno/quaderno-api
    for complete API documentation.
    """

    user_agent = 'QuadernoSdk/api-rest-sdk:' + __version__

    def __init__(self, token: str, api_host: str, version: str = None, ctype: str = 'json'):
        self.token = token
        self.ctype = ctype
        self.version = version
        self.host = api_host

    @property
    def headers(self):
        headers = {
            'User-Agent': self.user_agent
        }
        if self.version:
            headers.update({
                f'Accept': 'application/json; api_version={self.version}'
            })
        return headers

    def request(self, url: str, method: str, headers: dict = None, **kwargs) -> requests.Response:
        http_headers = self.headers
        http_headers.update(headers or {})

        response = requests.request(
            method, url,
            headers=http_headers,
            auth=(self.token, ''),
            **kwargs)

        if not (200 <= response.status_code < 300):
            raise QuadernoError(response)

        return response

    def _endpoint(self, action: str, method: str, **kwargs) -> requests.Response:
        return self.request(
            f'{self.host}/api/{action}.{self.ctype}', method, **kwargs)

    def get(self, action: str, params: dict = None, **kwargs) -> requests.Response:
        kwargs.update(params or {})
        return self._endpoint(action, 'GET', params=kwargs)

    def post(self, action: str, json: dict = None) -> requests.Response:
        return self._endpoint(action, 'POST', json=json)

    def put(self, action: str, json: dict = None) -> requests.Response:
        return self._endpoint(action, 'PUT', json=json)

    def delete(self, action: str, **kwargs) -> requests.Response:
        return self._endpoint(action, 'DELETE', **kwargs)

    def ping(self) -> requests.Response:
        return self.get('ping')

    def contacts(self, params: dict = None, **kwargs) -> requests.Response:
        """
        A contact is any client or vendor who appears
        on any of your invoices or expenses
        """
        return self.get('contacts', params=None, **kwargs)

    def post_contact(self, json: dict) -> requests.Response:
        return self.post('contacts', json)

    def get_contact(self, id: str) -> requests.Response:
        return self.get(f'contacts/{id}')

    def put_contact(self, id: str, json: dict) -> requests.Response:
        return self.put(f'contacts/{id}', json)

    def delete_contact(self, id: str) -> requests.Response:
        return self.delete(f'contacts/{id}')

    def invoices(self, params: dict = None, **kwargs) -> requests.Response:
        """
        An invoice is a detailed list of goods shipped or services rendered,
        with an account of all costs
        """
        return self.get('invoices', params=None, **kwargs)

    def post_invoice(self, json: dict) -> requests.Response:
        return self.post('invoices', json)

    def add_payment_to_invoice(self, id: str, json: dict) -> requests.Response:
        """
        When an invoice is paid, you can record the payment.
        """
        return self.post(f'invoices/{id}/payments', json)

    def drop_payment_from_invoice(self, id: str, payment_id: str) -> requests.Response:
        return self.delete(f'invoices/{id}/payments/{payment_id}')

    def get_invoice(self, id: str) -> requests.Response:
        return self.get(f'invoices/{id}')

    def put_invoice(self, id: str, json: dict) -> requests.Response:
        return self.put(f'invoices/{id}', json)

    def deliver_invoice(self, id: str) -> requests.Response:
        return self.get(f'invoices/{id}/deliver')

    def delete_invoice(self, id: str) -> requests.Response:
        return self.delete(f'invoices/{id}')

    def expenses(self, params: dict = None, **kwargs) -> requests.Response:
        """
        Expenses are all the invoices that you receive from your vendors
        """
        return self.get('expenses', params=None, **kwargs)

    def post_expense(self, json: dict) -> requests.Response:
        return self.post('expenses', json)

    def add_payment_to_expense(self, id: str, json: dict) -> requests.Response:
        """
        When an invoice is paid, you can record the payment.
        """
        return self.post(f'expenses/{id}/payments', json)

    def drop_payment_from_expense(self, id: str, payment_id: str) -> requests.Response:
        return self.delete(f'expenses/{id}/payments/{payment_id}')

    def get_expense(self, id: str) -> requests.Response:
        return self.get(f'expenses/{id}')

    def put_expense(self, id: str, json: dict) -> requests.Response:
        return self.put(f'expenses/{id}', json)

    def delete_expense(self, id: str) -> requests.Response:
        return self.delete(f'expenses/{id}')

    def estimates(self, params: dict = None, **kwargs) -> requests.Response:
        """
        An estimate is an offer that you give a client in order
        to get a specific job. With the time, estimates are usually
        turned into issued invoices.
        """
        return self.get('estimates', params=None, **kwargs)

    def post_estimate(self, json: dict) -> requests.Response:
        return self.post('estimates', json)

    def get_estimate(self, id: str) -> requests.Response:
        return self.get(f'estimates/{id}')

    def put_estimate(self, id: str, json: dict) -> requests.Response:
        return self.put(f'estimates/{id}', json)

    def deliver_estimate(self, id: str) -> requests.Response:
        return self.get(f'estimates/{id}/deliver')

    def delete_estimate(self, id: str) -> requests.Response:
        return self.delete(f'estimates/{id}')

    def credits(self, params: dict = None, **kwargs) -> requests.Response:
        """
        An credit is a detailed list of goods shipped or services rendered,
        with an account of all costs.
        """
        return self.get('credits', params=None, **kwargs)

    def post_credit(self, json: dict) -> requests.Response:
        return self.post('credits', json)

    def get_credit(self, id: str) -> requests.Response:
        return self.get(f'credits/{id}')

    def put_credit(self, id: str, json: dict) -> requests.Response:
        return self.put(f'credits/{id}', json)

    def deliver_credit(self, id: str) -> requests.Response:
        return self.get(f'credits/{id}/deliver')

    def delete_credit(self, id: str) -> requests.Response:
        return self.delete(f'credits/{id}')

    def recurring(self, params: dict = None, **kwargs) -> requests.Response:
        """
        A recurring is a special document that periodically renews itself
        and generating an recurring or an expense.
        """
        return self.get('recurring', params=None, **kwargs)

    def post_recurring(self, json: dict) -> requests.Response:
        return self.post('recurring', json)

    def get_recurring(self, id: str) -> requests.Response:
        return self.get(f'recurring/{id}')

    def put_recurring(self, id: str, json: dict) -> requests.Response:
        return self.put(f'recurring/{id}', json)

    def delete_recurring(self, id: str) -> requests.Response:
        return self.delete(f'recurring/{id}')

    def items(self, params: dict = None, **kwargs) -> requests.Response:
        """
        The items are those products or services that you
        sell to your customers.
        """
        return self.get('items', params=None, **kwargs)

    def post_item(self, json: dict) -> requests.Response:
        return self.post('items', json)

    def get_item(self, id: str) -> requests.Response:
        return self.get(f'items/{id}')

    def put_item(self, id: str, json: dict) -> requests.Response:
        return self.put(f'items/{id}', json)

    def delete_item(self, id: str) -> requests.Response:
        return self.delete(f'items/{id}')

    def webhooks(self, params: dict = None, **kwargs) -> requests.Response:
        """
        Quaderno Webhooks allows your aplication to receive information
        about document events as they occur.
        """
        return self.get('webhooks', params=None, **kwargs)

    def post_webhook(self, json: dict) -> requests.Response:
        return self.post('webhooks', json)

    def get_webhook(self, id: str) -> requests.Response:
        return self.get(f'webhooks/{id}')

    def put_webhook(self, id: str, json: dict) -> requests.Response:
        return self.put(f'webhooks/{id}', json)

    def delete_webhook(self, id: str) -> requests.Response:
        return self.delete(f'webhooks/{id}')

    def calculator(self, params: dict = None, **kwargs) -> requests.Response:
        """
        Calculate the taxes applied for a given customer data
        """
        return self.get('tax_rates/calculate', params, **kwargs)

    def get_charges(self, processor: str, id: str) -> requests.Response:
        return self.get(f'{processor}/charges/{id}')

    def get_refunds (self, processor: str, id: str) -> requests.Response:
        return self.get(f'{processor}/refunds/{id}')
