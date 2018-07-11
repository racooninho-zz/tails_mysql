import unittest
import json
import os
import utils


def get_request_files(file):
    cur_path = os.path.dirname(__file__)
    if file != 'prices':
        path_to_file = os.path.join(cur_path, "UnitTests\\" + file + ".json")
    else:
        path_to_file = os.path.join(cur_path, file + ".json")

    with open(path_to_file) as source_file:
        file = json.load(source_file)
    return file


request_without_USD = get_request_files("request_without_USD")
request_with_USD = get_request_files("request_with_USD")
final_result_from_request_without_USD = get_request_files("final_result_from_request_without_USD")
prices_file = get_request_files('prices')


class Tests(unittest.TestCase):
    def test_get_vat_bands(self):
        self.assertEqual(utils.get_vat_bands('standard'), 0.2)
        self.assertEqual(utils.get_vat_bands(''), 0)
        self.assertEqual(utils.get_vat_bands(True), 0)
        self.assertEqual(utils.get_vat_bands('rubish'), 0)

    def test_get_price_vat(self):
        self.assertEqual(utils.get_price_vat(1, prices_file['prices'])[0], {'product_id': 1,
                                                                           'price': 599, 'vat_band': 'standard'})

    def test_get_conversion_rate_from_api(self):
        self.assertEqual(utils.get_conversion_rate_from_api('GBP'), 1)
        self.assertNotEqual(utils.get_conversion_rate_from_api('EUR'), 10000)  # unless something extraordinary happens
        self.assertEqual(utils.get_conversion_rate_from_api('rubbish'), False)

    def test_get_conversion_currency(self):
        self.assertEqual(utils.get_conversion_currency(request_without_USD), (1, 'GBP'))

        # if there is no internet connection the following actually fails, due to the error handling in the solution
        self.assertNotEqual(utils.get_conversion_currency(request_with_USD), (1, 'GBP'))
        self.assertEqual(utils.get_conversion_currency('rubbish'), (1, 'GBP'))

    def test_get_int_round_value(self):
        self.assertEqual(utils.get_int_round_value(20), 20)
        self.assertEqual(utils.get_int_round_value(20.2432), 20)
        self.assertEqual(utils.get_int_round_value(20.8432), 21)
        self.assertEqual(utils.get_int_round_value('rubbish'), 0)

    def test_prepare_details(self):
        total_value_no_vat = 0
        vat_value = 0
        complete_order_details = []

        conversion, currency = utils.get_conversion_currency(request_without_USD)

        # prepare details return --- total_value_no_vat, vat_value, complete_order_details
        self.assertEqual(utils.prepare_details(complete_order_details,
                                              conversion, request_without_USD['order']['items'][0],
                                              total_value_no_vat, vat_value),
                         (599, 120, [{'product_id': 1, 'total': 599, 'vat': 120}]))

        complete_order_details = []
        conversion = 1.5  # simulate GBP-Dollar to be 1.5
        self.assertEqual(utils.prepare_details(complete_order_details,
                                              conversion, request_without_USD['order']['items'][0],
                                              total_value_no_vat, vat_value),
                         (898, 180, [{'product_id': 1, 'total': 898, 'vat': 180}]))
