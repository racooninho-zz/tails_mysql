from expiringdict import ExpiringDict
import json
import requests
import mysql.connector
import config


with open('prices.json') as f:
    data = json.load(f)

cache = ExpiringDict(max_len=200, max_age_seconds=3600)


def get_price_vat(product_id, source_dictionary):
    result = filter(lambda details: details['product_id'] == product_id, source_dictionary)
    return list(result)



def get_conversion_rate_from_api(currency):
    if cache.get(currency):
        return cache.get(currency)
    else:
        # in case you try to run the application without internet connection
        try:
            url = 'https://free.currencyconverterapi.com/api/v5/convert?q=GBP_' + currency + '&compact=ultra'
            result_from_api = requests.get(url)

            result_dict = json.loads(result_from_api.content.decode())

            if result_dict != {} and 'status' not in result_dict:
                # if api is 'overused' it will return a json message that includes the key 'status'
                cache[currency] = result_dict['GBP_'+currency]
                return result_dict['GBP_'+currency]
            else:
                return False
        except Exception:
            return False


def get_conversion_currency(currency):

    # deals with case that the currency parameter does not match any
    try:
        # check if the request has a currency parameter
        conversion_rate = get_conversion_rate_from_api(currency)
        if conversion_rate:
            result_currency = currency
        else:
            conversion_rate = 1
            result_currency = 'GBP'
    except TypeError:
        conversion_rate = 1
    return conversion_rate, result_currency


def get_vat_bands(bands):
    if bands == 'standard':
        return 0.2
    else:
        return 0


def prepare_details(complete_order_details, conversion, individual_item, total_value_no_vat, vat_value):
    #
    individual_order_details = {}
    product_id = individual_item['product_id']
    quantity = individual_item['quantity']

    # check if product exists in the prices.json

    details = get_price_vat(product_id, data['prices'])
    if details != []:
        details = details[0]
        applicable_vat = get_vat_bands(details['vat_band'])

        total_value_item_no_vat = get_int_round_value((quantity * details['price']) * conversion)
        total_value_no_vat += total_value_item_no_vat

        vat_item = get_int_round_value(((quantity * details['price']) * applicable_vat) * conversion)
        vat_value += vat_item

        individual_order_details.update({'product_id': details['product_id'], 'total': total_value_item_no_vat,
                                         "vat": vat_item})

        complete_order_details.append(individual_order_details)
        return total_value_no_vat, vat_value, complete_order_details
    else:
        return None

def get_int_round_value(number):

    # in cases someone tries to pass something other than a number, instead of breaking will return 0
    try:
        return int(round(number))
    except TypeError:
        return 0

class MySql:
    TABLE = ''

    def __init__(self, user, password, database, host):
        self.user = user
        self.password = password
        self.database = database
        self.host = host

    def get_connection(self):
        connection = mysql.connector.connect(user=self.user, password=self.password, database=self.database,
                                             host=self.host)
        return connection

    @classmethod
    def insert_single(cls, **kwargs):
        mysql_connection = MySql(config.mysql['user'], config.mysql['password'], config.mysql['db'],config.mysql['host'])
        connection = mysql_connection.get_connection()
        connection_cursor = connection.cursor()

        fields = ', '.join("{}".format(w) for w in kwargs.keys())
        values = ', '.join("'{}'".format(w) for w in kwargs.values())
        connection_cursor.execute(f"INSERT into {cls.TABLE} ({fields}) VALUES ({values})")

        connection.commit()

    @classmethod
    def select(cls, *args):
        mysql_connection = MySql((config.mysql['user'], config.mysql['password'], config.mysql['db'],
                                  config.mysql['host']))
        connection = mysql_connection.get_connection()
        connection_cursor = connection.cursor()

        fields = ', '.join("{}".format(w) for w in args)
        connection_cursor.execute(f"SELECT {fields} FROM {cls.TABLE}")
        result = connection_cursor.fetchall()
        return result

    @classmethod
    def update(cls, order_id, **kwargs):
        mysql_connection = MySql((config.mysql['user'], config.mysql['password'], config.mysql['db'],
                                  config.mysql['host']))
        connection = mysql_connection.get_connection()
        connection_cursor = connection.cursor()

        set_values = ', '.join(["%s = '%s'" % (key, value) for (key, value) in kwargs.items()])

        connection_cursor.execute(f"UPDATE {cls.TABLE} SET {set_values} WHERE OrderId = {order_id}")
        connection.commit()


class Orders(MySql):
    TABLE = "tails.orders"

