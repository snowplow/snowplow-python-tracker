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
import redis
import json
from snowplow_tracker import tracker, _version, consumer, subject
from httmock import all_requests, HTTMock

querystrings = [""]

default_consumer = consumer.Consumer("localhost", protocol="http", port=80)

default_subject = subject.Subject()

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
    return {
        "url": request.url,
        "status_code": 501
    }


class IntegrationTest(unittest.TestCase):

    def test_integration_page_view(self):
        t = tracker.Tracker(default_consumer, default_subject)
        with HTTMock(pass_response_content):
            t.track_page_view("http://savethearctic.org", "Save The Arctic", "http://referrer.com")
        expected_fields = {"e": "pv", "page": "Save+The+Arctic", "url": "http%3A%2F%2Fsavethearctic.org", "refr": "http%3A%2F%2Freferrer.com"}
        for key in expected_fields:
            self.assertEquals(from_querystring(key, querystrings[-1]), expected_fields[key])            

    def test_integration_ecommerce_transaction_item(self):
        t = tracker.Tracker(default_consumer, default_subject)
        with HTTMock(pass_response_content):
            t.track_ecommerce_transaction_item("12345", "pbz0025", 7.99, 2, "black-tarot", "tarot", currency="GBP")
        expected_fields = {"ti_ca": "tarot", "ti_id": "12345", "ti_qu": "2", "ti_sk": "pbz0025", "e": "ti", "ti_nm": "black-tarot", "ti_pr": "7.99", "ti_cu": "GBP"}
        for key in expected_fields:
            self.assertEquals(from_querystring(key, querystrings[-1]), expected_fields[key])

    def test_integration_ecommerce_transaction(self):
        t = tracker.Tracker(default_consumer, default_subject)
        with HTTMock(pass_response_content):
            t.track_ecommerce_transaction("6a8078be", 35, city="London", currency="GBP", items=
                [{  
                    "sku": "pbz0026",
                    "price": 20,
                    "quantity": 1
                },
                {
                    "sku": "pbz0038",
                    "price": 15,
                    "quantity": 1  
                }])

        expected_fields = {"e": "tr", "tr_id": "6a8078be", "tr_tt": "35", "tr_ci": "London", "tr_cu": "GBP"}
        for key in expected_fields:
            self.assertEquals(from_querystring(key, querystrings[-3]), expected_fields[key])

        expected_fields = {"e": "ti",  "ti_id": "6a8078be", "ti_sk": "pbz0026", "ti_pr": "20", "ti_cu": "GBP"}
        for key in expected_fields:
            self.assertEquals(from_querystring(key, querystrings[-2]), expected_fields[key])

        expected_fields = {"e": "ti",  "ti_id": "6a8078be", "ti_sk": "pbz0038", "ti_pr": "15", "ti_cu": "GBP"}
        for key in expected_fields:
            self.assertEquals(from_querystring(key, querystrings[-1]), expected_fields[key])

        self.assertEquals(from_querystring("dtm", querystrings[-3]), from_querystring("dtm", querystrings[-2]))

    def test_integration_screen_view(self):
        t = tracker.Tracker(default_consumer, default_subject)
        with HTTMock(pass_response_content):
            t.track_screen_view("Game HUD 2", "Hello!")
        expected_fields = {"e": "ue"}
        for key in expected_fields:          
            self.assertEquals(from_querystring(key, querystrings[-1]), expected_fields[key])

    def test_integration_struct_event(self):
        t = tracker.Tracker(default_consumer, default_subject)
        with HTTMock(pass_response_content):
            t.track_struct_event("Ecomm", "add-to-basket", "dog-skateboarding-video", "hd", 13.99)
        expected_fields = {"se_ca": "Ecomm", "se_pr": "hd", "se_la": "dog-skateboarding-video", "se_va": "13.99", "se_ac": "add-to-basket", "e": "se"}
        for key in expected_fields:
            self.assertEquals(from_querystring(key, querystrings[-1]), expected_fields[key])

    def test_integration_unstruct_event_non_base64(self):
        t = tracker.Tracker(default_consumer, default_subject, encode_base64=False)
        with HTTMock(pass_response_content):
            t.track_unstruct_event({"schema": "com.acme/viewed_product/json/2-0-2", "data": {"product_id": "ASO01043", "price$flt": 49.95, "walrus$tms": int(time.time() * 1000)}})
        expected_fields = {"e": "ue"}
        for key in expected_fields:
            self.assertEquals(from_querystring(key, querystrings[-1]), expected_fields[key])

    def test_integration_unstruct_event_base64(self):
        t = tracker.Tracker(default_consumer, default_subject)
        with HTTMock(pass_response_content):
            t.track_unstruct_event({"schema": "com.acme/viewed_product/json/2-0-2", "data": {"product_id": "ASO01043", "price$flt": 49.95, "walrus$tms": int(time.time() * 1000)}})
        expected_fields = {"e": "ue"}
        for key in expected_fields:
            self.assertEquals(from_querystring(key, querystrings[-1]), expected_fields[key])

    def test_integration_standard_nv_pairs(self):
        s = subject.Subject()
        s.set_platform("mob")
        s.set_user_id("user12345")
        s.set_screen_resolution(100, 200)
        s.set_color_depth(24)
        s.set_timezone("Europe London")
        s.set_lang("en")

        t = tracker.Tracker(consumer.Consumer("localhost"), s, "cf", app_id="angry-birds-android")
        with HTTMock(pass_response_content):
            t.track_page_view("localhost", "local host")
        expected_fields = {"tna": "cf", "evn": "com.snowplowanalytics", "res": "100x200",
                           "lang": "en", "aid": "angry-birds-android", "cd": "24", "tz": "Europe+London",
                           "p": "mob", "tv": "py-" + _version.__version__}
        for key in expected_fields:
            self.assertEquals(from_querystring(key, querystrings[-1]), expected_fields[key])

    def test_integration_redis_default(self):
        r = redis.StrictRedis()
        t = tracker.Tracker(consumer.RedisConsumer(), default_subject)
        t.track_page_view("http://www.example.com")
        event_string = r.rpop("snowplow")
        event_dict = json.loads(event_string.decode("utf-8"))
        self.assertEquals(event_dict["e"], "pv")

    def test_integration_redis_custom(self):
        r = redis.StrictRedis(db=1)
        t = tracker.Tracker(consumer.RedisConsumer(rdb=r, key="custom_key"), default_subject)
        t.track_page_view("http://www.example.com")
        event_string = r.rpop("custom_key")
        event_dict = json.loads(event_string.decode("utf-8"))
        self.assertEquals(event_dict["e"], "pv")

    def test_integration_success_callback(self):
        callback_success_queue = []
        callback_failure_queue = []
        callback_consumer = consumer.Consumer("localhost", on_success=lambda x: callback_success_queue.append(x),
                                                           on_failure=lambda x, y:callback_failure_queue.append(x))
        t = tracker.Tracker(callback_consumer, default_subject)
        with HTTMock(pass_response_content):
            t.track_page_view("http://www.example.com")
        self.assertEquals(callback_success_queue[0], 1)
        self.assertEquals(callback_failure_queue, [])

    def test_integration_failure_callback(self):
        callback_success_queue = []
        callback_failure_queue = []
        callback_consumer = consumer.Consumer("localhost", on_success=lambda x: callback_success_queue.append(x),
                                                           on_failure=lambda x, y:callback_failure_queue.append(x))
        t = tracker.Tracker(callback_consumer, default_subject)
        with HTTMock(fail_response_content):
            t.track_page_view("http://www.example.com")
        self.assertEquals(callback_success_queue, [])
        self.assertEquals(callback_failure_queue[0], 0)
