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
from snowplow_tracker import tracker
from httmock import all_requests, HTTMock

def from_querystring(field, url):
    pattern = re.compile("^[^#]*[?&]" + field + "=([^&#]*)")
    match = pattern.match(url)
    if match:
        return match.groups()[0]

@all_requests
def pass_response_content(url, request):
    return {
        "url": request.url,
        "status_code": 200
    }

@all_requests
def fail_response_content(url, request):
    return "HTTP status code [501] is a server error"


class IntegrationTest(unittest.TestCase):

    def test_integration_page_view(self):
        t = tracker.Tracker("localhost")
        with HTTMock(pass_response_content):
            val = t.track_page_view("http://savethearctic.org", "Save The Arctic", None)
            self.assertEquals(from_querystring("page", val), "Save+The+Arctic")

    def test_integration_ecommerce_transaction(self):
        t = tracker.Tracker("localhost")
        with HTTMock(pass_response_content):
            val = t.track_ecommerce_transaction("12345", 9.99, "Web", 1.98, 3.05, "London", "Denver", "Greenland")
            assertion_array = {"tr_tt": "9.99", "e": "tr", "tr_id": "12345", "tr_sh": "3.05", "tr_st": "Denver", "tr_af": "Web", "tr_co": "Greenland", "tr_tx": "1.98", "tr_ci": "London"}
            for key in assertion_array:
                self.assertEquals(from_querystring(key, val), assertion_array[key])

    def test_integration_ecommerce_transaction_item(self):
        t = tracker.Tracker("localhost")
        with HTTMock(pass_response_content):
            val = t.track_ecommerce_transaction_item("12345", "pbz0025", 7.99, 2, "black-tarot", "tarot")
            assertion_array = {"ti_ca": "tarot", "ti_id": "12345", "ti_qu": "2", "ti_sk": "pbz0025", "e": "ti", "ti_nm": "black-tarot", "ti_pr": "7.99"}
            for key in assertion_array:
                self.assertEquals(from_querystring(key, val), assertion_array[key])

    def test_integration_screen_view(self):
        t = tracker.Tracker("localhost")
        with HTTMock(pass_response_content):
            val = t.track_screen_view("Game HUD 2", "Hello!")
            assertion_array = {"e": "ue", "ue_na": "screen_view"}
            for key in assertion_array:
                self.assertEquals(from_querystring(key, val), assertion_array[key])            

    def test_integration_struct_event(self):
        t = tracker.Tracker("localhost")
        with HTTMock(pass_response_content):
            val = t.track_struct_event("Ecomm", "add-to-basket", "dog-skateboarding-video", "hd", 13.99)
            assertion_array = {"se_ca": "Ecomm", "se_pr": "hd", "se_la": "dog-skateboarding-video", "se_va": "13.99", "se_ac": "add-to-basket", "e": "se"}
            for key in assertion_array:
                self.assertEquals(from_querystring(key, val), assertion_array[key]) 


    def test_integration_unstruct_event_non_base64(self):
        t = tracker.Tracker("localhost")
        t.config["encode_base64"] = False
        with HTTMock(pass_response_content):
            val = t.track_unstruct_event("viewed_product", {"product_id": "ASO01043", "price$flt": 49.95, "walrus$tms": int(time.time() * 1000)})
            assertion_array = {"e": "ue", "ue_na": "viewed_product"}
            for key in assertion_array:
                self.assertEquals(from_querystring(key, val), assertion_array[key]) 

    def test_integration_unstruct_event_base64(self):
        t = tracker.Tracker("localhost")
        with HTTMock(pass_response_content):
            val = t.track_unstruct_event("viewed_product", {"product_id": "ASO01043", "price$flt": 49.95, "walrus$tms": int(time.time() * 1000)})
            assertion_array = {"e": "ue", "ue_na": "viewed_product"}
            for key in assertion_array:
                self.assertEquals(from_querystring(key, val), assertion_array[key]) 

    def test_integration_unstruct_event_non_base64_error(self):
        t = tracker.Tracker("localhost")
        t.config["encode_base64"] = False
        try:
            val = t.track_unstruct_event("viewed_product",
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
            val = t.track_unstruct_event("viewed_product",
                                         {
                                              "product_id": "ASO01043",
                                              "price$flt": 49.95,
                                              "walrus$tms": "hello",           # ERROR
                                         })
        except RuntimeError as e:
            self.assertEquals("walrus$tms in dict is not a tms", str(e))

    def test_integration_standard_nv_pairs(self):
        t = tracker.Tracker("localhost", "cf")
        t.set_platform("mob")
        t.set_user_id("user12345")
        t.set_app_id("angry-birds-android")
        t.set_screen_resolution(100, 200)
        t.set_color_depth(24)
        t.set_timezone("Europe London")
        t.set_lang("en")
        with HTTMock(pass_response_content):
            val = t.track_page_view("localhost", "local host", None)
            assertion_array = {"tna": "cf", "evn": "com.snowplowanalytics", "res": "100x200", "lang": "en", "aid": "angry-birds-android", "cd": "24", "tz": "Europe+London", "p": "mob", "tv": "py-0.2.0"}
            for key in assertion_array:
                self.assertEquals(from_querystring(key, val), assertion_array[key]) 
