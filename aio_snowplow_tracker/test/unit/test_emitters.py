"""
    test_emitters.py

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
import asyncio
import time
import unittest
import unittest.mock as mock
from freezegun import freeze_time
from typing import Any
from aiohttp import ServerTimeoutError

from aio_snowplow_tracker.emitters import Emitter, DEFAULT_MAX_LENGTH


# helpers
async def mocked_flush(*args: Any) -> None:
    pass


async def mocked_send_events(*args: Any) -> None:
    pass


async def mocked_http_success(*args: Any) -> bool:
    return True


async def mocked_http_failure(*args: Any) -> bool:
    return False


try:
    AsyncTestCase = unittest.IsolatedAsyncioTestCase
    async_patch = mock.patch
    async_mock = mock.AsyncMock
except AttributeError:
    # Python 3.7 compatibility
    import asynctest  # noqa
    AsyncTestCase = asynctest.TestCase
    async_patch = asynctest.patch
    async_mock = asynctest.create_autospec


class TestEmitters(AsyncTestCase):

    def setUp(self) -> None:
        pass

    def test_init(self) -> None:
        e = Emitter('0.0.0.0')
        self.assertEqual(e.endpoint, 'http://0.0.0.0/i')
        self.assertEqual(e.method, 'get')
        self.assertEqual(e.buffer_size, 1)
        self.assertEqual(e.buffer, [])
        self.assertIsNone(e.byte_limit)
        self.assertIsNone(e.bytes_queued)
        self.assertIsNone(e.on_success)
        self.assertIsNone(e.on_failure)
        self.assertIsNone(e.timer)
        self.assertIsNone(e.request_timeout)

    def test_init_buffer_size(self) -> None:
        e = Emitter('0.0.0.0', buffer_size=10)
        self.assertEqual(e.buffer_size, 10)

    def test_init_post(self) -> None:
        e = Emitter('0.0.0.0', method="post")
        self.assertEqual(e.buffer_size, DEFAULT_MAX_LENGTH)

    def test_init_byte_limit(self) -> None:
        e = Emitter('0.0.0.0', byte_limit=512)
        self.assertEqual(e.bytes_queued, 0)

    def test_init_requests_timeout(self) -> None:
        e = Emitter('0.0.0.0', request_timeout=(2.5, 5))
        self.assertEqual(e.request_timeout, (2.5, 5))

    def test_as_collector_uri(self) -> None:
        uri = Emitter.as_collector_uri('0.0.0.0')
        self.assertEqual(uri, 'http://0.0.0.0/i')

    def test_as_collector_uri_post(self) -> None:
        uri = Emitter.as_collector_uri('0.0.0.0', method="post")
        self.assertEqual(uri, 'http://0.0.0.0/com.snowplowanalytics.snowplow/tp2')

    def test_as_collector_uri_port(self) -> None:
        uri = Emitter.as_collector_uri('0.0.0.0', port=9090, method="post")
        self.assertEqual(uri, 'http://0.0.0.0:9090/com.snowplowanalytics.snowplow/tp2')

    def test_as_collector_uri_https(self) -> None:
        uri = Emitter.as_collector_uri('0.0.0.0', protocol="https")
        self.assertEqual(uri, 'https://0.0.0.0/i')

    def test_as_collector_uri_empty_string(self) -> None:
        with self.assertRaises(ValueError):
            Emitter.as_collector_uri('')

    @async_patch('aio_snowplow_tracker.Emitter.flush')
    async def test_input_no_flush(self, mok_flush: Any) -> None:
        mok_flush.side_effect = mocked_flush

        e = Emitter('0.0.0.0', method="get", buffer_size=2)
        nvPairs = {"n0": "v0", "n1": "v1"}
        await e.input(nvPairs)

        self.assertEqual(len(e.buffer), 1)
        self.assertDictEqual(nvPairs, e.buffer[0])
        self.assertIsNone(e.byte_limit)
        self.assertFalse(e.reached_limit())
        mok_flush.assert_not_called()

    @async_patch('aio_snowplow_tracker.Emitter.flush')
    async def test_input_flush_byte_limit(self, mok_flush: Any) -> None:
        mok_flush.side_effect = mocked_flush

        e = Emitter('0.0.0.0', method="get", buffer_size=2, byte_limit=16)
        nvPairs = {"n0": "v0", "n1": "v1"}
        await e.input(nvPairs)

        self.assertEqual(len(e.buffer), 1)
        self.assertDictEqual(nvPairs, e.buffer[0])
        self.assertTrue(e.reached_limit())
        self.assertEqual(mok_flush.call_count, 1)

    @async_patch('aio_snowplow_tracker.Emitter.flush')
    async def test_input_flush_buffer(self, mok_flush: Any) -> None:
        mok_flush.side_effect = mocked_flush

        e = Emitter('0.0.0.0', method="get", buffer_size=2, byte_limit=1024)
        nvPairs = {"n0": "v0", "n1": "v1"}
        await e.input(nvPairs)

        self.assertEqual(len(e.buffer), 1)
        self.assertFalse(e.reached_limit())
        self.assertDictEqual(nvPairs, e.buffer[0])

        nextPairs = {"n0": "v0"}
        await e.input(nextPairs)
        # since we mock flush, the buffer is not empty
        self.assertEqual(e.buffer, [nvPairs, nextPairs])
        self.assertTrue(e.reached_limit())
        self.assertEqual(mok_flush.call_count, 1)

    @async_patch('aio_snowplow_tracker.Emitter.flush')
    async def test_input_bytes_queued(self, mok_flush: Any) -> None:
        mok_flush.side_effect = mocked_flush

        e = Emitter('0.0.0.0', method="get", buffer_size=2, byte_limit=1024)
        nvPairs = {"n0": "v0", "n1": "v1"}
        await e.input(nvPairs)

        self.assertEqual(len(e.buffer), 1)
        self.assertEqual(e.bytes_queued, 24)

        await e.input(nvPairs)
        self.assertEqual(e.bytes_queued, 48)

    @async_patch('aio_snowplow_tracker.Emitter.flush')
    async def test_input_bytes_post(self, mok_flush: Any) -> None:
        mok_flush.side_effect = mocked_flush

        e = Emitter('0.0.0.0', method="post")
        nvPairs = {"testString": "test", "testNum": 2.72}
        await e.input(nvPairs)

        self.assertEqual(e.buffer, [{"testString": "test", "testNum": "2.72"}])

    @async_patch('aio_snowplow_tracker.Emitter.send_events')
    async def test_flush(self, mok_send_events: Any) -> None:
        mok_send_events.side_effect = mocked_send_events

        e = Emitter('0.0.0.0', buffer_size=2, byte_limit=None)
        nvPairs = {"n": "v"}
        await e.input(nvPairs)
        await e.input(nvPairs)

        self.assertEqual(mok_send_events.call_count, 1)
        self.assertEqual(len(e.buffer), 0)

    @async_patch('aio_snowplow_tracker.Emitter.send_events')
    async def test_flush_bytes_queued(self, mok_send_events: Any) -> None:
        mok_send_events.side_effect = mocked_send_events

        e = Emitter('0.0.0.0', buffer_size=2, byte_limit=256)
        nvPairs = {"n": "v"}
        await e.input(nvPairs)
        await e.input(nvPairs)

        self.assertEqual(mok_send_events.call_count, 1)
        self.assertEqual(len(e.buffer), 0)
        self.assertEqual(e.bytes_queued, 0)

    @freeze_time("2021-04-14 00:00:02")  # unix: 1618358402000
    def test_attach_sent_tstamp(self) -> None:
        e = Emitter('0.0.0.0')
        ev_list = [{"a": "aa"}, {"b": "bb"}, {"c": "cc"}]

        e.attach_sent_timestamp(ev_list)
        reduced = True
        for ev in ev_list:
            reduced = reduced and "stm" in ev.keys() and ev["stm"] == "1618358402000"
        self.assertTrue(reduced)

    @async_patch('aio_snowplow_tracker.Emitter.flush')
    async def test_flush_timer(self, mok_flush: Any) -> None:
        mok_flush.side_effect = mocked_flush

        e = Emitter('0.0.0.0', method="post", buffer_size=10)
        ev_list = [{"a": "aa"}, {"b": "bb"}, {"c": "cc"}]
        for i in ev_list:
            await e.input(i)

        await e.set_flush_timer(3)
        self.assertEqual(len(e.buffer), 3)
        await asyncio.sleep(5)
        self.assertEqual(mok_flush.call_count, 1)

    @async_patch('aio_snowplow_tracker.Emitter.flush')
    async def test_cancel_flush_timer(self, mok_flush: Any) -> None:
        mok_flush.side_effect = mocked_flush

        e = Emitter('0.0.0.0', method="post", buffer_size=10)
        ev_list = [{"a": "aa"}, {"b": "bb"}, {"c": "cc"}]
        for i in ev_list:
            await e.input(i)

        await e.set_flush_timer(3)
        self.assertEqual(len(e.buffer), 3)
        await asyncio.sleep(1)
        e.cancel_flush_timer()
        await asyncio.sleep(4)
        self.assertEqual(mok_flush.call_count, 0)

    @async_patch('aio_snowplow_tracker.Emitter.http_get')
    async def test_send_events_get_success(self, mok_http_get: Any) -> None:
        mok_http_get.side_effect = mocked_http_success
        mok_success = mock.Mock(return_value="success mocked")
        mok_failure = mock.Mock(return_value="failure mocked")

        e = Emitter('0.0.0.0', method="get", buffer_size=10, on_success=mok_success, on_failure=mok_failure)

        evBuffer = [{"a": "aa"}, {"b": "bb"}, {"c": "cc"}]
        await e.send_events(evBuffer)
        mok_success.assert_called_once_with(evBuffer)
        mok_failure.assert_not_called()

    @async_patch('aio_snowplow_tracker.Emitter.http_get')
    async def test_send_events_get_failure(self, mok_http_get: Any) -> None:
        mok_http_get.side_effect = mocked_http_failure
        mok_success = mock.Mock(return_value="success mocked")
        mok_failure = mock.Mock(return_value="failure mocked")

        e = Emitter('0.0.0.0', method="get", buffer_size=10, on_success=mok_success, on_failure=mok_failure)

        evBuffer = [{"a": "aa"}, {"b": "bb"}, {"c": "cc"}]
        await e.send_events(evBuffer)
        mok_success.assert_not_called()
        mok_failure.assert_called_once_with(0, evBuffer)

    @async_patch('aio_snowplow_tracker.Emitter.http_post')
    async def test_send_events_post_success(self, mok_http_post: Any) -> None:
        mok_http_post.side_effect = mocked_http_success
        mok_success = mock.Mock(return_value="success mocked")
        mok_failure = mock.Mock(return_value="failure mocked")

        e = Emitter('0.0.0.0', method="post", buffer_size=10, on_success=mok_success, on_failure=mok_failure)

        evBuffer = [{"a": "aa"}, {"b": "bb"}, {"c": "cc"}]
        await e.send_events(evBuffer)
        mok_success.assert_called_once_with(evBuffer)
        mok_failure.assert_not_called()

    @async_patch('aio_snowplow_tracker.Emitter.http_post')
    async def test_send_events_post_failure(self, mok_http_post: Any) -> None:
        mok_http_post.side_effect = mocked_http_failure
        mok_success = mock.Mock(return_value="success mocked")
        mok_failure = mock.Mock(return_value="failure mocked")

        e = Emitter('0.0.0.0', method="post", buffer_size=10, on_success=mok_success, on_failure=mok_failure)

        evBuffer = [{"a": "aa"}, {"b": "bb"}, {"c": "cc"}]
        await e.send_events(evBuffer)
        mok_success.assert_not_called()
        mok_failure.assert_called_with(0, evBuffer)

    @async_patch('aio_snowplow_tracker.emitters.aiohttp.ClientSession.get')
    async def test_http_get_successful(self, mok_get_request: Any) -> None:
        mok_get_request.return_value.__aenter__.return_value = mock.Mock(status=200)
        e = Emitter('0.0.0.0')
        get_succeeded = await e.http_get({"a": "b"})

        self.assertTrue(get_succeeded)

    @async_patch('aio_snowplow_tracker.emitters.aiohttp.ClientSession.post')
    async def test_http_get_successful(self, mok_post_request: Any) -> None:
        mok_post_request.return_value.__aenter__.return_value = mock.Mock(status=200)
        e = Emitter('0.0.0.0')
        get_succeeded = await e.http_post({"a": "b"})

        self.assertTrue(get_succeeded)

    @async_patch('aio_snowplow_tracker.emitters.aiohttp.ClientSession.post')
    async def test_http_post_connect_timeout_error(self, mok_post_request: Any) -> None:
        mok_post_request.side_effect = ServerTimeoutError
        e = Emitter('0.0.0.0')
        post_succeeded = await e.http_post("dummy_string")

        self.assertFalse(post_succeeded)

    @async_patch('aio_snowplow_tracker.emitters.aiohttp.ClientSession.get')
    async def test_http_get_connect_timeout_error(self, mok_get_request: Any) -> None:
        mok_get_request.side_effect = ServerTimeoutError
        e = Emitter('0.0.0.0')
        get_succeeded = await e.http_get({"a": "b"})

        self.assertFalse(get_succeeded)

    @async_patch('aio_snowplow_tracker.Emitter.http_post')
    async def test_async_send_events_post_success(self, mok_http_post: Any) -> None:
        mok_http_post.side_effect = mocked_http_success
        mok_success = mock.Mock(return_value="success mocked")
        mok_failure = mock.Mock(return_value="failure mocked")

        ae = Emitter('0.0.0.0', method="post", buffer_size=10, on_success=mok_success, on_failure=mok_failure)

        evBuffer = [{"a": "aa"}, {"b": "bb"}, {"c": "cc"}]
        await ae.send_events(evBuffer)
        mok_success.assert_called_once_with(evBuffer)
        mok_failure.assert_not_called()

    @async_patch('aio_snowplow_tracker.Emitter.http_post')
    async def test_async_send_events_post_failure(self, mok_http_post: Any) -> None:
        mok_http_post.side_effect = mocked_http_failure
        mok_success = mock.Mock(return_value="success mocked")
        mok_failure = mock.Mock(return_value="failure mocked")

        ae = Emitter('0.0.0.0', method="post", buffer_size=10, on_success=mok_success, on_failure=mok_failure)

        evBuffer = [{"a": "aa"}, {"b": "bb"}, {"c": "cc"}]
        await ae.send_events(evBuffer)
        mok_success.assert_not_called()
        mok_failure.assert_called_with(0, evBuffer)
