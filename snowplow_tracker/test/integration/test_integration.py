"""
    test_integration.py

    Copyright (c) 2013-2014 Snowplow Analytics Ltd. All rights reserved.

    This program is licensed to you under the Apache License Version 2.0,
    and you may not use this file except in compliance with the Apache License
    Version 2.0. You may obtain a copy of the Apache License Version 2.0 at
    http://www.apache.org/licenses/LICENSE-2.0.

    Unless required by applicable law or agreed to in writing,
    software distributed under the Apache License Version 2.0 is distributed on
    an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
    express or implied. See the Apache License Version 2.0 for the specific
    language governing permissions and limitations there under.

    Authors: Anuj More, Alex Dean, Fred Blundun
    Copyright: Copyright (c) 2013-2014 Snowplow Analytics Ltd
    License: Apache License Version 2.0
"""

import unittest
import time
import re
from snowplow_tracker import tracker, _version
from httmock import all_requests, HTTMock

querystrings = [""]

def from_querystring(field, url):
    pattern = re.compile("^[^#]*[?&]" + field + "=([^&#]*)")
    match = pattern.match(url)
    if match:
        return match.groups()[0]

@all_requests
def pass_response_content(url, request):
    querystrings.append(request.url)
    return {
        "url": request.url,
        "status_code": 200
    }

@all_requests
def fail_response_content(url, request):
    return (False, 501)


class IntegrationTest(unittest.TestCase):

    def test_integration_page_view(self):
        t = tracker.Tracker("localhost")
        with HTTMock(pass_response_content):
            t.track_page_view("http://savethearctic.org", "Save The Arctic", None)
            self.assertEquals(from_querystring("page", querystrings[-1]),"Save+The+Arctic")

    def test_integration_ecommerce_transaction(self):
        t = tracker.Tracker("localhost")
        with HTTMock(pass_response_content):
            t.track_ecommerce_transaction("12345", 9.99, "Web", 1.98, 3.05, "Sacramento", "California", "USA")
            expected_fields = {"tr_tt": "9.99", "e": "tr", "tr_id": "12345", "tr_sh": "3.05", "tr_st": "California", "tr_af": "Web", "tr_co": "USA", "tr_tx": "1.98", "tr_ci": "Sacramento"}
            for key in expected_fields:
                self.assertEquals(from_querystring(key, querystrings[-1]), expected_fields[key])

    def test_integration_ecommerce_transaction_item(self):
        t = tracker.Tracker("localhost")
        with HTTMock(pass_response_content):
            t.track_ecommerce_transaction_item("12345", "pbz0025", 7.99, 2, "black-tarot", "tarot", ti_currency="GBP")
            expected_fields = {"ti_ca": "tarot", "ti_id": "12345", "ti_qu": "2", "ti_sk": "pbz0025", "e": "ti", "ti_nm": "black-tarot", "ti_pr": "7.99", "ti_cu": "GBP"}
            for key in expected_fields:
                self.assertEquals(from_querystring(key, querystrings[-1]), expected_fields[key])

    def test_integration_screen_view(self):
        t = tracker.Tracker("localhost")
        with HTTMock(pass_response_content):
            t.track_screen_view("Game HUD 2", "Hello!")
            expected_fields = {"e": "ue", "ue_na": "screen_view"}
            for key in expected_fields:          
                self.assertEquals(from_querystring(key, querystrings[-1]), expected_fields[key])

    def test_integration_struct_event(self):
        t = tracker.Tracker("localhost")
        with HTTMock(pass_response_content):
            t.track_struct_event("Ecomm", "add-to-basket", "dog-skateboarding-video", "hd", 13.99)
            expected_fields = {"se_ca": "Ecomm", "se_pr": "hd", "se_la": "dog-skateboarding-video", "se_va": "13.99", "se_ac": "add-to-basket", "e": "se"}
            for key in expected_fields:
                self.assertEquals(from_querystring(key, querystrings[-1]), expected_fields[key])


    def test_integration_unstruct_event_non_base64(self):
        t = tracker.Tracker("localhost", encode_base64=False)
        with HTTMock(pass_response_content):
            t.track_unstruct_event("viewed_product", {"product_id": "ASO01043", "price$flt": 49.95, "walrus$tms": int(time.time() * 1000)})
            expected_fields = {"e": "ue", "ue_na": "viewed_product"}
            for key in expected_fields:
                self.assertEquals(from_querystring(key, querystrings[-1]), expected_fields[key])

    def test_integration_unstruct_event_base64(self):
        t = tracker.Tracker("localhost")
        with HTTMock(pass_response_content):
            t.track_unstruct_event("viewed_product", {"product_id": "ASO01043", "price$flt": 49.95, "walrus$tms": int(time.time() * 1000)})
            expected_fields = {"e": "ue", "ue_na": "viewed_product"}
            for key in expected_fields:
                self.assertEquals(from_querystring(key, querystrings[-1]), expected_fields[key])

    def test_integration_unstruct_event_non_base64_error(self):
        t = tracker.Tracker("localhost", encode_base64=False)
        try:
            t.track_unstruct_event("viewed_product",
                               {
                                   "product_id": "ASO01043",
                                   "price$flt": 49,                 # ERROR
                                   "walrus$tms": int(time.time() * 1000),
                               })
        except RuntimeError as e:
            self.assertEquals("price$flt in dict is not a flt", str(e))


    def test_integration_unstruct_event_base64_error(self):
        t = tracker.Tracker("localhost")
        try:
            t.track_unstruct_event("viewed_product",
                                         {
                                              "product_id": "ASO01043",
                                              "price$flt": 49.95,
                                              "walrus$tms": "hello",           # ERROR
                                         })
        except RuntimeError as e:
            self.assertEquals("walrus$tms in dict is not a tms", str(e))

    def test_integration_standard_nv_pairs(self):
        t = tracker.Tracker("localhost", "cf", app_id="angry-birds-android")
        t.set_platform("mob")
        t.set_user_id("user12345")
        t.set_screen_resolution(100, 200)
        t.set_color_depth(24)
        t.set_timezone("Europe London")
        t.set_lang("en")
        with HTTMock(pass_response_content):
            t.track_page_view("localhost", "local host", None)
            expected_fields = {"tna": "cf", "evn": "com.snowplowanalytics", "res": "100x200", "lang": "en", "aid": "angry-birds-android", "cd": "24", "tz": "Europe+London", "p": "mob", "tv": "py-" + _version.__version__}
            for key in expected_fields:
                self.assertEquals(from_querystring(key, querystrings[-1]), expected_fields[key])

    def test_integration_transaction(self):
        t = tracker.Tracker("localhost")
        with HTTMock(pass_response_content):
            t.track_transaction(
                {"order_id": "6a8078be",
                 "tr_total_value": 45,
                 "tr_city": "London", 
                 "tr_currency": "GBP"},

                [{  
                    "ti_id": "6a8078be",
                    "ti_sku": "pbz0026",
                    "ti_price": 20,
                    "ti_quantity": 1
                },
                {
                    "ti_id": "6a8078be",
                    "ti_sku": "pbz0038",
                    "ti_price": 15,
                    "ti_quantity": 1  
                }])

            expected_fields = {"e": "tr", "tr_id": "6a8078be", "tr_tt": "45", "tr_ci": "London", "tr_cu": "GBP"}
            for key in expected_fields:
                self.assertEquals(from_querystring(key, querystrings[-3]), expected_fields[key])

            expected_fields = {"e": "ti",  "ti_id": "6a8078be", "ti_sk": "pbz0026", "ti_pr": "20", "ti_cu": "GBP"}
            for key in expected_fields:
                self.assertEquals(from_querystring(key, querystrings[-2]), expected_fields[key])

            expected_fields = {"e": "ti",  "ti_id": "6a8078be", "ti_sk": "pbz0038", "ti_pr": "15", "ti_cu": "GBP"}
            for key in expected_fields:
                self.assertEquals(from_querystring(key, querystrings[-1]), expected_fields[key])

            for key in ["dtm", "tid"]:
                self.assertEquals(from_querystring(key, querystrings[-3]), from_querystring(key, querystrings[-2]))
