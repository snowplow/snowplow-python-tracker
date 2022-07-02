"""
    test_integration.py

    Copyright (c) 2013-2021 Snowplow Analytics Ltd. All rights reserved.

    This program is licensed to you under the Apache License Version 2.0,
    and you may not use this file except in compliance with the Apache License
    Version 2.0. You may obtain a copy of the Apache License Version 2.0 at
    http://www.apache.org/licenses/LICENSE-2.0.

    Unless required by applicable law or agreed to in writing,
    software distributed under the Apache License Version 2.0 is distributed on
    an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
    express or implied. See the Apache License Version 2.0 for the specific
    language governing permissions and limitations there under.

    Authors: Anuj More, Alex Dean, Fred Blundun, Paul Boocock
    Copyright: Copyright (c) 2013-2021 Snowplow Analytics Ltd
    License: Apache License Version 2.0
"""

import re
import json
import base64
from urllib.parse import unquote_plus

import aiohttp
import aiohttp.web
import pytest
from aiohttp.test_utils import TestServer
from freezegun import freeze_time
from typing import Dict, Optional

from snowplow_tracker import tracker, _version, emitters, subject
from snowplow_tracker.self_describing_json import SelfDescribingJson
from snowplow_tracker.redis import redis_emitter


@pytest.fixture
def default_subject():
    return subject.Subject()


@pytest.fixture
async def snowplow_server(aiohttp_server) -> TestServer:
    async def track(request):
        if 'requests' not in request.app:
            request.app['requests'] = []
        request.app['requests'].append(request)
        # Calling read() here ensures the request content is available in the test method.
        await request.read()

        return aiohttp.web.Response(body=b'Thanks for the data!')

    app = aiohttp.web.Application()
    app.router.add_get('/i', track)
    app.router.add_post('/com.snowplowanalytics.snowplow/tp2', track)
    return await aiohttp_server(app)


@pytest.fixture
async def snowplow_server_failure(aiohttp_server) -> TestServer:
    async def successful_response(request):
        return aiohttp.web.Response(body=b'Simulating an internal server error', status=501)

    app = aiohttp.web.Application()
    app.router.add_get('/i', successful_response)
    app.router.add_post('/com.snowplowanalytics.snowplow/tp2', successful_response)
    return await aiohttp_server(app)


def create_emitter(snowplow_server: TestServer, **kwargs):
    return emitters.Emitter(snowplow_server.host, protocol='http', port=snowplow_server.port, **kwargs)


async def test_integration_page_view(snowplow_server: TestServer, default_subject: subject.Subject):
    t = tracker.Tracker([create_emitter(snowplow_server)], default_subject)
    await t.track_page_view("http://savethearctic.org", "Save The Arctic", "http://referrer.com")

    expected = {"e": "pv", "page": "Save The Arctic", "url": "http://savethearctic.org", "refr": "http://referrer.com"}
    assert expected.items() <= snowplow_server.app['requests'][-1].query.items()


async def test_integration_ecommerce_transaction_item(snowplow_server: TestServer, default_subject):
    t = tracker.Tracker([create_emitter(snowplow_server)], default_subject)
    await t.track_ecommerce_transaction_item("12345", "pbz0025", 7.99, 2, "black-tarot", "tarot", currency="GBP")
    expected_fields = {"ti_ca": "tarot", "ti_id": "12345", "ti_qu": "2", "ti_sk": "pbz0025", "e": "ti",
                       "ti_nm": "black-tarot", "ti_pr": "7.99", "ti_cu": "GBP"}
    assert expected_fields.items() <= snowplow_server.app['requests'][-1].query.items()


async def test_integration_ecommerce_transaction(snowplow_server: TestServer, default_subject: subject.Subject):
    t = tracker.Tracker([create_emitter(snowplow_server)], default_subject)
    await t.track_ecommerce_transaction(
        "6a8078be", 35, city="London", currency="GBP",
        items=[
            {
                "sku": "pbz0026",
                "price": 20,
                "quantity": 1
            },
            {
                "sku": "pbz0038",
                "price": 15,
                "quantity": 1
            }])

    queries_dicts = [r.query for r in snowplow_server.app['requests']]
    queries = [q.items() for q in queries_dicts]

    assert queries[-3] >= {"e": "tr", "tr_id": "6a8078be", "tr_tt": "35", "tr_ci": "London", "tr_cu": "GBP"}.items()
    assert queries[-2] >= {"e": "ti", "ti_id": "6a8078be", "ti_sk": "pbz0026", "ti_pr": "20", "ti_cu": "GBP"}.items()
    assert queries[-1] >= {"e": "ti", "ti_id": "6a8078be", "ti_sk": "pbz0038", "ti_pr": "15", "ti_cu": "GBP"}.items()
    assert queries_dicts[-3]['ttm'] == queries_dicts[-2]['ttm']


async def test_integration_screen_view(snowplow_server: TestServer, default_subject: subject.Subject):
    t = tracker.Tracker([create_emitter(snowplow_server)], default_subject, encode_base64=False)
    await t.track_screen_view("Game HUD 2", id_="534")

    query_dict = snowplow_server.app['requests'][-1].query
    assert {"e": "ue"}.items() <= query_dict.items()
    assert json.loads(query_dict["ue_pr"]) == {
        "schema": "iglu:com.snowplowanalytics.snowplow/unstruct_event/jsonschema/1-0-0",
        "data": {
            "schema": "iglu:com.snowplowanalytics.snowplow/screen_view/jsonschema/1-0-0",
            "data": {
                "name": "Game HUD 2",
                "id": "534",
            }
        }
    }


async def test_integration_struct_event(snowplow_server: TestServer, default_subject: subject.Subject):
    t = tracker.Tracker([create_emitter(snowplow_server)], default_subject)
    await t.track_struct_event("Ecomm", "add-to-basket", "dog-skateboarding-video", "hd", 13.99)

    query_dict = snowplow_server.app['requests'][-1].query
    expect = {"se_ca": "Ecomm", "se_pr": "hd", "se_la": "dog-skateboarding-video", "se_va": "13.99",
              "se_ac": "add-to-basket", "e": "se"}
    assert query_dict.items() >= expect.items()


async def test_integration_unstruct_event_non_base64(snowplow_server: TestServer, default_subject: subject.Subject):
    t = tracker.Tracker([create_emitter(snowplow_server)], default_subject, encode_base64=False)
    product_data = {"product_id": "ASO01043", "price$flt": 49.95, "walrus$tms": 1000}
    await t.track_unstruct_event(SelfDescribingJson("iglu:com.acme/viewed_product/jsonschema/2-0-2", product_data))

    query_dict = snowplow_server.app['requests'][-1].query
    assert {"e": "ue"}.items() <= query_dict.items()
    assert json.loads(query_dict["ue_pr"]) == {
        "schema": "iglu:com.snowplowanalytics.snowplow/unstruct_event/jsonschema/1-0-0",
        "data": {"schema": "iglu:com.acme/viewed_product/jsonschema/2-0-2", "data": product_data},
    }


async def test_integration_unstruct_event_base64(snowplow_server: TestServer, default_subject: subject.Subject):
    t = tracker.Tracker([create_emitter(snowplow_server)], default_subject, encode_base64=True)
    product_data = {"product_id": "ASO01043", "price$flt": 49.95, "walrus$tms": 1000}
    await t.track_unstruct_event(SelfDescribingJson("iglu:com.acme/viewed_product/jsonschema/2-0-2", product_data))

    query_dict = snowplow_server.app['requests'][-1].query
    assert query_dict["e"] == "ue"
    envelope = json.loads((base64.urlsafe_b64decode(bytearray(query_dict["ue_px"], "utf-8"))).decode("utf-8"))
    assert envelope == {
        "schema": "iglu:com.snowplowanalytics.snowplow/unstruct_event/jsonschema/1-0-0",
        "data": {"schema": "iglu:com.acme/viewed_product/jsonschema/2-0-2", "data": product_data},
    }


async def test_integration_context_non_base64(snowplow_server: TestServer, default_subject: subject.Subject):
    t = tracker.Tracker([create_emitter(snowplow_server)], default_subject, encode_base64=False)
    await t.track_page_view("localhost", "local host", None, [
        SelfDescribingJson("iglu:com.example/user/jsonschema/2-0-3", {"user_type": "tester"})])

    query_dict = snowplow_server.app['requests'][-1].query
    envelope = json.loads(unquote_plus(query_dict["co"]))
    assert envelope == {
        "schema": "iglu:com.snowplowanalytics.snowplow/contexts/jsonschema/1-0-1",
        "data": [{"schema": "iglu:com.example/user/jsonschema/2-0-3", "data": {"user_type": "tester"}}],
    }


async def test_integration_context_base64(snowplow_server: TestServer, default_subject: subject.Subject):
    t = tracker.Tracker([create_emitter(snowplow_server)], default_subject, encode_base64=True)
    await t.track_page_view("localhost", "local host", None, [
        SelfDescribingJson("iglu:com.example/user/jsonschema/2-0-3", {"user_type": "tester"})])

    query_dict = snowplow_server.app['requests'][-1].query
    envelope = json.loads((base64.urlsafe_b64decode(bytearray(query_dict["cx"], "utf-8"))).decode("utf-8"))
    assert envelope == {
        "schema": "iglu:com.snowplowanalytics.snowplow/contexts/jsonschema/1-0-1",
        "data": [{"schema": "iglu:com.example/user/jsonschema/2-0-3", "data": {"user_type": "tester"}}]
    }


async def test_integration_standard_nv_pairs(snowplow_server: TestServer):
    s = subject.Subject()
    s.set_platform("mob")
    s.set_user_id("user12345")
    s.set_screen_resolution(100, 200)
    s.set_color_depth(24)
    s.set_timezone("Europe London")
    s.set_lang("en")

    t = tracker.Tracker([create_emitter(snowplow_server)], s, "cf", app_id="angry-birds-android")
    await t.track_page_view("localhost", "local host")

    query_dict = snowplow_server.app['requests'][-1].query
    expected_fields = {
        "tna": "cf", "res": "100x200", "lang": "en", "aid": "angry-birds-android", "cd": "24", "tz": "Europe London",
        "p": "mob", "tv": "py-" + _version.__version__}
    assert query_dict.items() >= expected_fields.items()
    assert query_dict["eid"] is not None
    assert query_dict["dtm"] is not None


async def test_integration_identification_methods(snowplow_server: TestServer):
    s = subject.Subject()
    s.set_domain_user_id("4616bfb38f872d16")
    s.set_ip_address("255.255.255.255")
    s.set_useragent("Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)")
    s.set_network_user_id("fbc6c76c-bce5-43ce-8d5a-31c5")

    t = tracker.Tracker([create_emitter(snowplow_server)], s, "cf", app_id="angry-birds-android")
    await t.track_page_view("localhost", "local host")

    assert snowplow_server.app['requests'][-1].query.items() >= {
        "duid": "4616bfb38f872d16",
        "ip": "255.255.255.255",
        "ua": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)",
        "tnuid": "fbc6c76c-bce5-43ce-8d5a-31c5",
    }.items()


async def test_integration_event_subject(snowplow_server: TestServer):
    s = subject.Subject()
    s.set_domain_user_id("4616bfb38f872d16")
    s.set_ip_address("255.255.255.255")

    t = tracker.Tracker([create_emitter(snowplow_server)], s, "cf", app_id="angry-birds-android")
    evSubject = subject.Subject().set_domain_user_id("1111aaa11a111a11").set_lang("EN")
    await t.track_page_view("localhost", "local host", event_subject=evSubject)

    assert snowplow_server.app['requests'][-1].query.items() >= {
        "duid": "1111aaa11a111a11",
        "lang": "EN"
    }.items()


@pytest.mark.parametrize(
    "emitter_kwargs,expected_key",
    [
        ({}, 'snowplow'),
        ({'key': 'custom_key'}, 'custom_key'),
    ],
)
async def test_integration_redis_custom(emitter_kwargs: Dict, expected_key: str, default_subject: subject.Subject):
    try:
        import fakeredis
        r = fakeredis.FakeStrictRedis()
        t = tracker.Tracker([redis_emitter.RedisEmitter(rdb=r, **emitter_kwargs)], default_subject)
        await t.track_page_view("http://www.example.com")
        event_string = r.rpop(expected_key)
        event_dict = json.loads(event_string.decode("utf-8"))
        assert event_dict["e"] == "pv"
    except ImportError:
        with pytest.raises(RuntimeError):
            redis_emitter.RedisEmitter()


async def test_integration_success_callback(snowplow_server: TestServer, default_subject: subject.Subject):
    callback_success_queue = []
    callback_failure_queue = []
    callback_emitter = create_emitter(
        snowplow_server,
        on_success=lambda x: callback_success_queue.append(x),
        on_failure=lambda x, y: callback_failure_queue.append(x))
    t = tracker.Tracker([callback_emitter], default_subject)
    await t.track_page_view("http://www.example.com")

    expected = {
        "e": "pv",
        "url": "http://www.example.com",
    }
    assert len(callback_success_queue) == 1
    for k in expected.keys():
        assert callback_success_queue[0][0][k] == expected[k]
    assert callback_failure_queue == []


async def test_integration_failure_callback(snowplow_server_failure: TestServer, default_subject: subject.Subject):
    callback_success_queue = []
    callback_failure_queue = []
    callback_emitter = create_emitter(
        snowplow_server_failure,
        on_success=lambda x: callback_success_queue.append(x),
        on_failure=lambda x, y: callback_failure_queue.append(x))
    t = tracker.Tracker([callback_emitter], default_subject)
    await t.track_page_view("http://www.example.com")
    assert callback_success_queue == []
    assert callback_failure_queue[0] == 0


async def test_post_page_view(snowplow_server: TestServer, default_subject: subject.Subject):
    t = tracker.Tracker([create_emitter(snowplow_server, method='post', buffer_size=1)], default_subject)
    await t.track_page_view("localhost", "local host", None)

    request = snowplow_server.app['requests'][-1]
    assert request.method == 'POST'
    data = await request.json()
    assert data["schema"] == "iglu:com.snowplowanalytics.snowplow/payload_data/jsonschema/1-0-4"
    assert data['data'][0].items() >= {"e": "pv", "page": "local host", "url": "localhost"}.items()


async def test_post_batched(snowplow_server: TestServer, default_subject: subject.Subject):
    t = tracker.Tracker(create_emitter(snowplow_server, method='post', buffer_size=2), default_subject)
    await t.track_struct_event("Test", "A")
    await t.track_struct_event("Test", "B")

    data = await snowplow_server.app['requests'][-1].json()
    assert data["data"][0]["se_ac"] == "A"
    assert data["data"][1]["se_ac"] == "B"


@freeze_time("2021-04-19 00:00:01")  # unix: 1618790401000
async def test_timestamps(snowplow_server: TestServer, default_subject: subject.Subject):
    t = tracker.Tracker([create_emitter(snowplow_server, method='post', buffer_size=3)], default_subject)
    await t.track_page_view("localhost", "stamp0", None, tstamp=None)
    await t.track_page_view("localhost", "stamp1", None, tstamp=1358933694000)
    await t.track_page_view("localhost", "stamp2", None, tstamp=1358933694000.00)

    data = await snowplow_server.app['requests'][-1].json()
    expected_timestamps = [
        {"dtm": "1618790401000", "ttm": None, "stm": "1618790401000"},
        {"dtm": "1618790401000", "ttm": "1358933694000", "stm": "1618790401000"},
        {"dtm": "1618790401000", "ttm": "1358933694000", "stm": "1618790401000"}
    ]

    for i, event in enumerate(expected_timestamps):
        for attr in ("dtm", "ttm", "stm"):
            assert data["data"][i].get(attr) == expected_timestamps[i][attr]


async def test_bytelimit(snowplow_server: TestServer, default_subject: subject.Subject):
    post_emitter = create_emitter(snowplow_server, method='post', buffer_size=5, byte_limit=420)
    t = tracker.Tracker([post_emitter], default_subject)
    await t.track_struct_event("Test", "A")  # 140 bytes
    await t.track_struct_event("Test", "A")  # 280 bytes
    await t.track_struct_event("Test", "A")  # 420 bytes. Send
    await t.track_struct_event("Test", "AA")  # 141

    data = await snowplow_server.app['requests'][-1].json()
    assert len(data["data"]) == 3
    assert post_emitter.bytes_queued == 136 + len(_version.__version__)


async def test_unicode_get(snowplow_server: TestServer, default_subject: subject.Subject):
    t = tracker.Tracker([create_emitter(snowplow_server)], default_subject, encode_base64=False)
    unicode_a = u'\u0107'
    unicode_b = u'test.\u0107om'
    test_ctx = SelfDescribingJson('iglu:a.b/c/jsonschema/1-0-0', {'test': unicode_a})
    await t.track_page_view(unicode_b, context=[test_ctx])
    await t.track_screen_view(unicode_b, context=[test_ctx])

    page_view_query = snowplow_server.app['requests'][-2].query
    assert page_view_query["url"] == unicode_b

    screen_view_query = snowplow_server.app['requests'][-1].query
    assert unicode_a == json.loads(screen_view_query["co"])['data'][0]['data']['test']
    assert unicode_b == json.loads(screen_view_query["ue_pr"])['data']['data']['name']


async def test_unicode_post(snowplow_server: TestServer, default_subject: subject.Subject):
    post_emitter = create_emitter(snowplow_server, method='post', buffer_size=1)
    t = tracker.Tracker([post_emitter], default_subject, encode_base64=False)
    unicode_a = u'\u0107'
    unicode_b = u'test.\u0107om'
    test_ctx = SelfDescribingJson('iglu:a.b/c/jsonschema/1-0-0', {'test': unicode_a})
    await t.track_page_view(unicode_b, context=[test_ctx])
    await t.track_screen_view(unicode_b, context=[test_ctx])

    page_view_event = await snowplow_server.app['requests'][-2].json()
    assert unicode_b == page_view_event['data'][0]['url']
    assert unicode_a == json.loads(page_view_event['data'][0]['co'])['data'][0]['data']['test']

    screen_view_event = await snowplow_server.app['requests'][-1].json()
    assert unicode_b == json.loads(screen_view_event['data'][0]['ue_pr'])['data']['data']['name']
