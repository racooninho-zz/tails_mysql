# External imports
import tornado.ioloop
import tornado.web

# Project imports
import utils

# Python imports
import os
import json
import time

class Order(tornado.web.RequestHandler):
    def post(self):

        #initialise transaction details
        total_value_no_vat = 0
        vat_value = 0
        complete_order_details = []

        details_dictionary = json.loads(self.request.body)

        currency = self.get_argument('currency', None)
        if not currency:
            if 'currency' in details_dictionary['order']:
                currency = details_dictionary['order']['currency']

            else:
                currency = 'GBP'

        conversion, currency = utils.get_conversion_currency(currency)



        for individual_item in details_dictionary['order']['items']:

            result = utils.prepare_details(complete_order_details, conversion, individual_item,
                                           total_value_no_vat, vat_value)
            if result:
                total_value_no_vat, vat_value, complete_order_details = result


        # MYSQL INTEGRATION
        arguments = {"OrderId": details_dictionary['order']['id'],
                     "OrderDetails": json.dumps(details_dictionary),
                     "TimeStamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                     "OrderStatus": "Preparing",
                     "Currency": currency,
                     "ConversionRateFromGBP": conversion,
                     "TotalOrder": total_value_no_vat,
                     "TotalVat": int(round(vat_value)),
                     "TotalWithVat": total_value_no_vat + vat_value,
                     "OrderItemDetails": json.dumps(complete_order_details)
                     }
        utils.Orders.insert_single(**arguments)
        ##


        self.write({"order_id": details_dictionary['order']['id'],
                    "currency": currency,
                    "rate_GBP-" + currency: conversion,
                    "total_order": total_value_no_vat,
                    "total_vat": int(round(vat_value)),
                    "total_with_vat": total_value_no_vat+vat_value,
                    "order_details": complete_order_details})


