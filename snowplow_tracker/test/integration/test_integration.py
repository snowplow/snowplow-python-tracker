'''
    test_integration.py

    Copyright (c) 2013-2014 Snowplow Analytics Ltd. All rights reserved.

    This program is licensed to you under the Apache License Version 2.0,
    and you may not use this file except in compliance with the Apache License
    Version 2.0. You may obtain a copy of the Apache License Version 2.0 at
    http://www.apache.org/licenses/LICENSE-2.0.

    Unless required by applicable law or agreed to in writing,
    software distributed under the Apache License Version 2.0 is distributed on
    an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
    express or implied. See the Apache License Version 2.0 for the specific
    language governing permissions and limitations there under.

    Authors: Anuj More, Alex Dean
    Copyright: Copyright (c) 2013-2014 Snowplow Analytics Ltd
    License: Apache License Version 2.0
'''

import unittest
import time
from snowplow_tracker import tracker
from httmock import all_requests, HTTMock


@all_requests
def pass_response_content(url, request):
    return 'True'


@all_requests
def fail_response_content(url, request):
    return 'HTTP status code [501] is a server error'


class IntegrationTest(unittest.TestCase):

    def test_integration_page_view(self):
        t = tracker.Tracker.hostname('localhost')
        with HTTMock(pass_response_content):
            val = t.track_page_view('http://savethearctic.org', 'Save The Arctic', None)
            self.assertTrue(val)

    def test_integration_ecommerce_transaction(self):
        t = tracker.Tracker.hostname('localhost')
        with HTTMock(pass_response_content):
            val = t.track_ecommerce_transaction('12345', 'Web', 9.99, 1.98, 3.00, 'London', 'Denver', 'Greenland')
            self.assertTrue(val)

    def test_integration_ecommerce_transaction_item(self):
        t = tracker.Tracker.hostname('localhost')
        with HTTMock(pass_response_content):
            val = t.track_ecommerce_transaction_item('12345', 'pbz0025', 'black-tarot', 'tarot', 7.99, 2)
            self.assertTrue(val)

    def test_integration_screen_view(self):
        t = tracker.Tracker.hostname('localhost')
        with HTTMock(pass_response_content):
            val = t.track_screen_view('Game HUD 2', 'Hello!')
            self.assertTrue(val)

    def test_integration_struct_event(self):
        t = tracker.Tracker.hostname('localhost')
        with HTTMock(pass_response_content):
            val = t.track_struct_event('Ecomm', 'add-to-basket', 'dog-skateboarding-video', 'hd', 13.99)
            self.assertTrue(val)

    def test_integration_unstruct_event_non_base64(self):
        t = tracker.Tracker.hostname('localhost')
        t.config['encode_base64'] = False
        with HTTMock(pass_response_content):
            val = t.track_unstruct_event('viewed_product', {'product_id': 'ASO01043', 'price$flt': 49.95, 'walrus$tms': int(time.time() * 1000),})
            self.assertTrue(val)

    def test_integration_unstruct_event_base64(self):
        t = tracker.Tracker.hostname('localhost')
        with HTTMock(pass_response_content):
            val = t.track_unstruct_event('viewed_product', {'product_id': 'ASO01043', 'price$flt': 49.95, 'walrus$tms': int(time.time() * 1000),})
            self.assertTrue(val)

    def test_integration_unstruct_event_non_base64_error(self):
        t = tracker.Tracker.hostname('localhost')
        t.config['encode_base64'] = False
        try:
            val = t.track_unstruct_event('viewed_product',
                               {
                                   'product_id': 'ASO01043',
                                   'price$flt': 49,                 # ERROR
                                   'walrus$tms': int(time.time() * 1000),
                               })
        except RuntimeError as e:
            self.assertEquals("price$flt in dict is not a flt", str(e))


    def test_integration_unstruct_event_base64_error(self):
        t = tracker.Tracker.hostname('localhost')
        try:
            val = t.track_unstruct_event('viewed_product',
                                         {
                                              'product_id': 'ASO01043',
                                              'price$flt': 49.95,
                                              'walrus$tms': 'hello',           # ERROR
                                         })
        except RuntimeError as e:
            self.assertEquals("walrus$tms in dict is not a tms", str(e))
