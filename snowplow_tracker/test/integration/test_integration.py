# """
#     test_integration.py

#     Copyright (c) 2013-2023 Snowplow Analytics Ltd. All rights reserved.

#     This program is licensed to you under the Apache License Version 2.0,
#     and you may not use this file except in compliance with the Apache License
#     Version 2.0. You may obtain a copy of the Apache License Version 2.0 at
#     http://www.apache.org/licenses/LICENSE-2.0.

#     Unless required by applicable law or agreed to in writing,
#     software distributed under the Apache License Version 2.0 is distributed on
#     an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#     express or implied. See the Apache License Version 2.0 for the specific
#     language governing permissions and limitations there under.

#     Authors: Anuj More, Alex Dean, Fred Blundun, Jack Keene, Paul Boocock
#     Copyright: Copyright (c) 2013-2023 Snowplow Analytics Ltd
#     License: Apache License Version 2.0
# """

import unittest
import re
import json
import base64
from urllib.parse import unquote_plus
import pytest
from httmock import all_requests, HTTMock
from freezegun import freeze_time
from typing import Any, Dict, Optional

from snowplow_tracker import tracker, _version, emitters, subject
from snowplow_tracker.self_describing_json import SelfDescribingJson
from snowplow_tracker.redis import redis_emitter


querystrings = [""]

default_emitter = emitters.Emitter("localhost", protocol="http", port=80, batch_size=1)

get_emitter = emitters.Emitter("localhost", protocol="http", port=80, method="get")

default_subject = subject.Subject()


def from_querystring(field: str, url: str) -> Optional[str]:
    pattern = re.compile("^[^#]*[?&]" + field + "=([^&#]*)")
    match = pattern.match(url)
    if match:
        return match.groups()[0]


@all_requests
def pass_response_content(url: str, request: Any) -> Dict[str, Any]:
    querystrings.append(request.url)
    return {"url": request.url, "status_code": 200}


@all_requests
def pass_post_response_content(url: str, request: Any) -> Dict[str, Any]:
    querystrings.append(json.loads(request.body))
    return {"url": request.url, "status_code": 200}


@all_requests
def fail_response_content(url: str, request: Any) -> Dict[str, Any]:
    return {"url": request.url, "status_code": 501}


class IntegrationTest(unittest.TestCase):
    def test_integration_page_view(self) -> None:
        t = tracker.Tracker([get_emitter], default_subject)
        with HTTMock(pass_response_content):
            t.track_page_view(
                "http://savethearctic.org", "Save The Arctic", "http://referrer.com"
            )
        expected_fields = {
            "e": "pv",
            "page": "Save+The+Arctic",
            "url": "http%3A%2F%2Fsavethearctic.org",
            "refr": "http%3A%2F%2Freferrer.com",
        }
        for key in expected_fields:
            self.assertEqual(
                from_querystring(key, querystrings[-1]), expected_fields[key]
            )

    def test_integration_ecommerce_transaction_item(self) -> None:
        t = tracker.Tracker([get_emitter], default_subject)
        with HTTMock(pass_response_content):
            t.track_ecommerce_transaction_item(
                "12345", "pbz0025", 7.99, 2, "black-tarot", "tarot", currency="GBP"
            )
        expected_fields = {
            "ti_ca": "tarot",
            "ti_id": "12345",
            "ti_qu": "2",
            "ti_sk": "pbz0025",
            "e": "ti",
            "ti_nm": "black-tarot",
            "ti_pr": "7.99",
            "ti_cu": "GBP",
        }
        for key in expected_fields:
            self.assertEqual(
                from_querystring(key, querystrings[-1]), expected_fields[key]
            )

    def test_integration_ecommerce_transaction(self) -> None:
        t = tracker.Tracker([get_emitter], default_subject)
        with HTTMock(pass_response_content):
            t.track_ecommerce_transaction(
                "6a8078be",
                35,
                city="London",
                currency="GBP",
                items=[
                    {"sku": "pbz0026", "price": 20, "quantity": 1},
                    {"sku": "pbz0038", "price": 15, "quantity": 1},
                ],
            )

        expected_fields = {
            "e": "tr",
            "tr_id": "6a8078be",
            "tr_tt": "35",
            "tr_ci": "London",
            "tr_cu": "GBP",
        }
        for key in expected_fields:
            self.assertEqual(
                from_querystring(key, querystrings[-3]), expected_fields[key]
            )

        expected_fields = {
            "e": "ti",
            "ti_id": "6a8078be",
            "ti_sk": "pbz0026",
            "ti_pr": "20",
            "ti_cu": "GBP",
        }
        for key in expected_fields:
            self.assertEqual(
                from_querystring(key, querystrings[-2]), expected_fields[key]
            )

        expected_fields = {
            "e": "ti",
            "ti_id": "6a8078be",
            "ti_sk": "pbz0038",
            "ti_pr": "15",
            "ti_cu": "GBP",
        }
        for key in expected_fields:
            self.assertEqual(
                from_querystring(key, querystrings[-1]), expected_fields[key]
            )

        self.assertEqual(
            from_querystring("ttm", querystrings[-3]),
            from_querystring("ttm", querystrings[-2]),
        )

    def test_integration_mobile_screen_view(self) -> None:
        t = tracker.Tracker([get_emitter], default_subject, encode_base64=False)
        with HTTMock(pass_response_content):
            t.track_mobile_screen_view("534", "Game HUD 2")
        expected_fields = {"e": "ue"}
        for key in expected_fields:
            self.assertEqual(
                from_querystring(key, querystrings[-1]), expected_fields[key]
            )
        envelope_string = from_querystring("ue_pr", querystrings[-1])
        envelope = json.loads(unquote_plus(envelope_string))
        self.assertEqual(
            envelope,
            {
                "schema": "iglu:com.snowplowanalytics.snowplow/unstruct_event/jsonschema/1-0-0",
                "data": {
                    "schema": "iglu:com.snowplowanalytics.mobile/screen_view/jsonschema/1-0-0",
                    "data": {"id": "534", "name": "Game HUD 2"},
                },
            },
        )

    def test_integration_struct_event(self) -> None:
        t = tracker.Tracker([get_emitter], default_subject)
        with HTTMock(pass_response_content):
            t.track_struct_event(
                "Ecomm", "add-to-basket", "dog-skateboarding-video", "hd", 13.99
            )
        expected_fields = {
            "se_ca": "Ecomm",
            "se_pr": "hd",
            "se_la": "dog-skateboarding-video",
            "se_va": "13.99",
            "se_ac": "add-to-basket",
            "e": "se",
        }
        for key in expected_fields:
            self.assertEqual(
                from_querystring(key, querystrings[-1]), expected_fields[key]
            )

    def test_integration_self_describing_event_non_base64(self) -> None:
        t = tracker.Tracker([get_emitter], default_subject, encode_base64=False)
        with HTTMock(pass_response_content):
            t.track_self_describing_event(
                SelfDescribingJson(
                    "iglu:com.acme/viewed_product/jsonschema/2-0-2",
                    {"product_id": "ASO01043", "price$flt": 49.95, "walrus$tms": 1000},
                )
            )
        expected_fields = {"e": "ue"}
        for key in expected_fields:
            self.assertEqual(
                from_querystring(key, querystrings[-1]), expected_fields[key]
            )
        envelope_string = from_querystring("ue_pr", querystrings[-1])
        envelope = json.loads(unquote_plus(envelope_string))
        self.assertEqual(
            envelope,
            {
                "schema": "iglu:com.snowplowanalytics.snowplow/unstruct_event/jsonschema/1-0-0",
                "data": {
                    "schema": "iglu:com.acme/viewed_product/jsonschema/2-0-2",
                    "data": {
                        "product_id": "ASO01043",
                        "price$flt": 49.95,
                        "walrus$tms": 1000,
                    },
                },
            },
        )

    def test_integration_self_describing_event_base64(self) -> None:
        t = tracker.Tracker([get_emitter], default_subject, encode_base64=True)
        with HTTMock(pass_response_content):
            t.track_self_describing_event(
                SelfDescribingJson(
                    "iglu:com.acme/viewed_product/jsonschema/2-0-2",
                    {"product_id": "ASO01043", "price$flt": 49.95, "walrus$tms": 1000},
                )
            )
        expected_fields = {"e": "ue"}
        for key in expected_fields:
            self.assertEqual(
                from_querystring(key, querystrings[-1]), expected_fields[key]
            )
        envelope_string = unquote_plus(from_querystring("ue_px", querystrings[-1]))
        envelope = json.loads(
            (base64.urlsafe_b64decode(bytearray(envelope_string, "utf-8"))).decode(
                "utf-8"
            )
        )
        self.assertEqual(
            envelope,
            {
                "schema": "iglu:com.snowplowanalytics.snowplow/unstruct_event/jsonschema/1-0-0",
                "data": {
                    "schema": "iglu:com.acme/viewed_product/jsonschema/2-0-2",
                    "data": {
                        "product_id": "ASO01043",
                        "price$flt": 49.95,
                        "walrus$tms": 1000,
                    },
                },
            },
        )

    def test_integration_context_non_base64(self) -> None:
        t = tracker.Tracker([get_emitter], default_subject, encode_base64=False)
        with HTTMock(pass_response_content):
            t.track_page_view(
                "localhost",
                "local host",
                None,
                [
                    SelfDescribingJson(
                        "iglu:com.example/user/jsonschema/2-0-3",
                        {"user_type": "tester"},
                    )
                ],
            )
        envelope_string = from_querystring("co", querystrings[-1])
        envelope = json.loads(unquote_plus(envelope_string))
        self.assertEqual(
            envelope,
            {
                "schema": "iglu:com.snowplowanalytics.snowplow/contexts/jsonschema/1-0-1",
                "data": [
                    {
                        "schema": "iglu:com.example/user/jsonschema/2-0-3",
                        "data": {"user_type": "tester"},
                    }
                ],
            },
        )

    def test_integration_context_base64(self) -> None:
        t = tracker.Tracker([get_emitter], default_subject, encode_base64=True)
        with HTTMock(pass_response_content):
            t.track_page_view(
                "localhost",
                "local host",
                None,
                [
                    SelfDescribingJson(
                        "iglu:com.example/user/jsonschema/2-0-3",
                        {"user_type": "tester"},
                    )
                ],
            )
        envelope_string = unquote_plus(from_querystring("cx", querystrings[-1]))
        envelope = json.loads(
            (base64.urlsafe_b64decode(bytearray(envelope_string, "utf-8"))).decode(
                "utf-8"
            )
        )
        self.assertEqual(
            envelope,
            {
                "schema": "iglu:com.snowplowanalytics.snowplow/contexts/jsonschema/1-0-1",
                "data": [
                    {
                        "schema": "iglu:com.example/user/jsonschema/2-0-3",
                        "data": {"user_type": "tester"},
                    }
                ],
            },
        )

    def test_integration_standard_nv_pairs(self) -> None:
        s = subject.Subject()
        s.set_platform("mob")
        s.set_user_id("user12345")
        s.set_screen_resolution(100, 200)
        s.set_color_depth(24)
        s.set_timezone("Europe London")
        s.set_lang("en")

        t = tracker.Tracker(
            [emitters.Emitter("localhost", method="get")],
            s,
            "cf",
            app_id="angry-birds-android",
        )
        with HTTMock(pass_response_content):
            t.track_page_view("localhost", "local host")
        expected_fields = {
            "tna": "cf",
            "res": "100x200",
            "lang": "en",
            "aid": "angry-birds-android",
            "cd": "24",
            "tz": "Europe+London",
            "p": "mob",
            "tv": "py-" + _version.__version__,
        }
        for key in expected_fields:
            self.assertEqual(
                from_querystring(key, querystrings[-1]), expected_fields[key]
            )
        self.assertIsNotNone(from_querystring("eid", querystrings[-1]))
        self.assertIsNotNone(from_querystring("dtm", querystrings[-1]))

    def test_integration_identification_methods(self) -> None:
        s = subject.Subject()
        s.set_domain_user_id("4616bfb38f872d16")
        s.set_domain_session_id("59ed13b1a5724dae")
        s.set_domain_session_index(1)
        s.set_ip_address("255.255.255.255")
        s.set_useragent(
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)"
        )
        s.set_network_user_id("fbc6c76c-bce5-43ce-8d5a-31c5")

        t = tracker.Tracker(
            [emitters.Emitter("localhost", method="get")],
            s,
            "cf",
            app_id="angry-birds-android",
        )
        with HTTMock(pass_response_content):
            t.track_page_view("localhost", "local host")
        expected_fields = {
            "duid": "4616bfb38f872d16",
            "sid": "59ed13b1a5724dae",
            "vid": "1",
            "ip": "255.255.255.255",
            "ua": "Mozilla%2F5.0+%28compatible%3B+MSIE+9.0%3B+Windows+NT+6.0%3B+Trident%2F5.0%29",
            "tnuid": "fbc6c76c-bce5-43ce-8d5a-31c5",
        }
        for key in expected_fields:
            self.assertEqual(
                from_querystring(key, querystrings[-1]), expected_fields[key]
            )

    def test_integration_event_subject(self) -> None:
        s = subject.Subject()
        s.set_domain_user_id("4616bfb38f872d16")
        s.set_lang("ES")

        t = tracker.Tracker(
            [emitters.Emitter("localhost", method="get")],
            s,
            "cf",
            app_id="angry-birds-android",
        )
        evSubject = (
            subject.Subject().set_domain_user_id("1111aaa11a111a11").set_lang("EN")
        )
        with HTTMock(pass_response_content):
            t.track_page_view("localhost", "local host", event_subject=evSubject)
        expected_fields = {"duid": "1111aaa11a111a11", "lang": "EN"}
        for key in expected_fields:
            self.assertEqual(
                from_querystring(key, querystrings[-1]), expected_fields[key]
            )

    def test_integration_redis_default(self) -> None:
        try:
            import fakeredis

            r = fakeredis.FakeStrictRedis()
            t = tracker.Tracker([redis_emitter.RedisEmitter(rdb=r)], default_subject)
            t.track_page_view("http://www.example.com")
            event_string = r.rpop("snowplow")
            event_dict = json.loads(event_string.decode("utf-8"))
            self.assertEqual(event_dict["e"], "pv")
        except ImportError:
            with pytest.raises(RuntimeError):
                redis_emitter.RedisEmitter()

    def test_integration_redis_custom(self) -> None:
        try:
            import fakeredis

            r = fakeredis.FakeStrictRedis()
            t = tracker.Tracker(
                [redis_emitter.RedisEmitter(rdb=r, key="custom_key")], default_subject
            )
            t.track_page_view("http://www.example.com")
            event_string = r.rpop("custom_key")
            event_dict = json.loads(event_string.decode("utf-8"))
            self.assertEqual(event_dict["e"], "pv")
        except ImportError:
            with pytest.raises(RuntimeError):
                redis_emitter.RedisEmitter("arg", key="kwarg")

    def test_integration_success_callback(self) -> None:
        callback_success_queue = []
        callback_failure_queue = []
        callback_emitter = emitters.Emitter(
            "localhost",
            method="get",
            on_success=lambda x: callback_success_queue.append(x),
            on_failure=lambda x, y: callback_failure_queue.append(x),
        )
        t = tracker.Tracker([callback_emitter], default_subject)
        with HTTMock(pass_response_content):
            t.track_page_view("http://www.example.com")
        expected = {
            "e": "pv",
            "url": "http://www.example.com",
        }
        self.assertEqual(len(callback_success_queue), 1)
        for k in expected.keys():
            self.assertEqual(callback_success_queue[0][0][k], expected[k])
        self.assertEqual(callback_failure_queue, [])

    def test_integration_failure_callback(self) -> None:
        callback_success_queue = []
        callback_failure_queue = []
        callback_emitter = emitters.Emitter(
            "localhost",
            method="get",
            on_success=lambda x: callback_success_queue.append(x),
            on_failure=lambda x, y: callback_failure_queue.append(x),
        )
        t = tracker.Tracker([callback_emitter], default_subject)
        with HTTMock(fail_response_content):
            t.track_page_view("http://www.example.com")
        self.assertEqual(callback_success_queue, [])
        self.assertEqual(callback_failure_queue[0], 0)

    def test_post_page_view(self) -> None:
        t = tracker.Tracker([default_emitter], default_subject)
        with HTTMock(pass_post_response_content):
            t.track_page_view("localhost", "local host", None)
        expected_fields = {"e": "pv", "page": "local host", "url": "localhost"}
        request = querystrings[-1]
        self.assertEqual(
            request["schema"],
            "iglu:com.snowplowanalytics.snowplow/payload_data/jsonschema/1-0-4",
        )
        for key in expected_fields:
            self.assertEqual(request["data"][0][key], expected_fields[key])

    def test_post_batched(self) -> None:
        default_emitter = emitters.Emitter(
            "localhost", protocol="http", port=80, batch_size=2
        )
        t = tracker.Tracker(default_emitter, default_subject)
        with HTTMock(pass_post_response_content):
            t.track_struct_event("Test", "A")
            t.track_struct_event("Test", "B")
        self.assertEqual(querystrings[-1]["data"][0]["se_ac"], "A")
        self.assertEqual(querystrings[-1]["data"][1]["se_ac"], "B")

    @freeze_time("2021-04-19 00:00:01")  # unix: 1618790401000
    def test_timestamps(self) -> None:
        emitter = emitters.Emitter("localhost", protocol="http", port=80, batch_size=3)
        t = tracker.Tracker([emitter], default_subject)
        with HTTMock(pass_post_response_content):
            t.track_page_view("localhost", "stamp0", None, tstamp=None)
            t.track_page_view("localhost", "stamp1", None, tstamp=1358933694000)
            t.track_page_view("localhost", "stamp2", None, tstamp=1358933694000.00)

        expected_timestamps = [
            {"dtm": "1618790401000", "ttm": None, "stm": "1618790401000"},
            {"dtm": "1618790401000", "ttm": "1358933694000", "stm": "1618790401000"},
            {"dtm": "1618790401000", "ttm": "1358933694000", "stm": "1618790401000"},
        ]
        request = querystrings[-1]

        for i, event in enumerate(expected_timestamps):
            self.assertEqual(
                request["data"][i].get("dtm"), expected_timestamps[i]["dtm"]
            )
            self.assertEqual(
                request["data"][i].get("ttm"), expected_timestamps[i]["ttm"]
            )
            self.assertEqual(
                request["data"][i].get("stm"), expected_timestamps[i]["stm"]
            )

    def test_bytelimit(self) -> None:
        default_emitter = emitters.Emitter(
            "localhost", protocol="http", port=80, batch_size=5, byte_limit=420
        )
        t = tracker.Tracker(default_emitter, default_subject)
        with HTTMock(pass_post_response_content):
            t.track_struct_event("Test", "A")  # 140 bytes
            t.track_struct_event("Test", "A")  # 280 bytes
            t.track_struct_event("Test", "A")  # 420 bytes. Send
            t.track_struct_event("Test", "AA")  # 141
        self.assertEqual(len(querystrings[-1]["data"]), 3)
        self.assertEqual(default_emitter.bytes_queued, 136 + len(_version.__version__))

    def test_unicode_get(self) -> None:
        t = tracker.Tracker([get_emitter], default_subject, encode_base64=False)
        unicode_a = "\u0107"
        unicode_b = "test.\u0107om"
        test_ctx = SelfDescribingJson(
            "iglu:a.b/c/jsonschema/1-0-0", {"test": unicode_a}
        )
        with HTTMock(pass_response_content):
            t.track_page_view(unicode_b, context=[test_ctx])
            t.track_mobile_screen_view(unicode_b, context=[test_ctx])

        url_string = unquote_plus(from_querystring("url", querystrings[-2]))
        try:
            self.assertEqual(url_string.decode("utf-8"), unicode_b)
        except AttributeError:
            # in python 3: str type contains unicode (so no 'decode')
            self.assertEqual(url_string, unicode_b)

        context_string = unquote_plus(from_querystring("co", querystrings[-1]))
        actual_a = json.loads(context_string)["data"][0]["data"]["test"]
        self.assertEqual(actual_a, unicode_a)

        uepr_string = unquote_plus(from_querystring("ue_pr", querystrings[-1]))
        actual_b = json.loads(uepr_string)["data"]["data"]["id"]
        self.assertEqual(actual_b, unicode_b)

    def test_unicode_post(self) -> None:
        t = tracker.Tracker([default_emitter], default_subject, encode_base64=False)
        unicode_a = "\u0107"
        unicode_b = "test.\u0107om"
        test_ctx = SelfDescribingJson(
            "iglu:a.b/c/jsonschema/1-0-0", {"test": unicode_a}
        )
        with HTTMock(pass_post_response_content):
            t.track_page_view(unicode_b, context=[test_ctx])
            t.track_mobile_screen_view(unicode_b, context=[test_ctx])

        pv_event = querystrings[-2]
        self.assertEqual(pv_event["data"][0]["url"], unicode_b)

        in_test_ctx = json.loads(pv_event["data"][0]["co"])["data"][0]["data"]["test"]
        self.assertEqual(in_test_ctx, unicode_a)

        sv_event = querystrings[-1]
        in_uepr_name = json.loads(sv_event["data"][0]["ue_pr"])["data"]["data"]["id"]
        self.assertEqual(in_uepr_name, unicode_b)
