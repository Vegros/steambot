import json
from currency_converter import CurrencyConverter


class Handler:
    def __init__(self, game_name):
        self.game_name = game_name
        self.response = self.load_json()
        self.is_on_discount = False

    def load_json(self):
        try:
            with open(f'{self.game_name}.json', 'r') as json_file:
                data = json.load(json_file)
            return data

        except Exception as e:
            print(e)
            return {}

    def convert_to_euros(self, amount, from_currency):
        c = CurrencyConverter()
        euros = c.convert(amount, 'EUR', from_currency)
        return euros

    def get_dev(self):
        if self.response:
            return ", ".join(self.response.get("developers", "developer not found"))
        return 'json file not found'

    def get_summary(self):
        if self.response:
            return "".join(self.response.get("short_description", "summary is not found"))
        return 'json file not found'

    def get_price(self):
        if self.response:
            value = str(self.response.get("price_overview", {}).get("final", None))
            currency = str(self.response.get("price_overview", {}).get("currency", None))
            eur = value[:-2]
            cents = value[-2:]
            final_price = float(eur + "." + cents)
            euros = self.convert_to_euros(final_price, currency)

            # check discount
            discount = str(self.response.get("price_overview", {}).get("discount_percent", None))
            if discount != '0':
                self.is_on_discount = True

            return f"EUR {euros:.2f}"
        return 'json file not found'
