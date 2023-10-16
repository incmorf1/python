import json
import requests
from iso4217 import Currency


class CurrencyFind:
    def __init__(self):
        self.kek = None
        self.url = 'https://api.monobank.ua/bank/currency'

    def set_vars(self, vars):
        self.kek = vars

    def show(self, summ):
        name = summ[-3:]
        currency = self.find_currency_by_name(name)
        if name.isdigit():
            return "Number was received"
        elif currency is not None:
            bank_data = self.get_data()
            return self.search_in_mono_data(bank_data, currency)
        else:
            return "no such currency"

    @staticmethod
    def search_in_mono_data(bank_data, currency):
        if currency == 980:
            return bank_data
        else:
            result = [item for item in bank_data if item.get("currencyCodeA") == currency]
            return result

    def get_data(self):

        data = requests.request(
            method='GET',
            url=self.url,
            headers={'Accept': 'application/json'}
        ).json()

        if 'errorDescription' in data:  # and data['errorDescription'] == 'Too many requests':
            with open('localappdata.json', 'r') as local_file:
                return json.load(local_file)
        else:
            with open('localappdata.json', 'w') as local_file:
                json.dump(data, local_file, indent=4)
            return data

    @staticmethod
    def save_convert_to_file(data):
        try:
            with open('database.json', 'r') as file:
                existing_data = json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            existing_data = []

        existing_data.append(data)

        with open('database.json', 'w') as file:
            json.dump(existing_data, file, indent=4)

    @staticmethod
    def find_currency_by_name(name):
        try:
            code = Currency[name.lower()]
            return code.number
        except KeyError:
            return None

    @staticmethod
    def find_currency_by_code(code):
        for currency in Currency:
            if currency.number == code:
                return currency.name
