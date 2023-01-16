# """
#     test_emitters.py

#     Copyright (c) 2013-2022 Snowplow Analytics Ltd. All rights reserved.

#     This program is licensed to you under the Apache License Version 2.0,
#     and you may not use this file except in compliance with the Apache License
#     Version 2.0. You may obtain a copy of the Apache License Version 2.0 at
#     http://www.apache.org/licenses/LICENSE-2.0.

#     Unless required by applicable law or agreed to in writing,
#     software distributed under the Apache License Version 2.0 is distributed on
#     an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#     express or implied. See the Apache License Version 2.0 for the specific
#     language governing permissions and limitations there under.

#     Authors: Anuj More, Alex Dean, Fred Blundun, Paul Boocock
#     Copyright: Copyright (c) 2013-2022 Snowplow Analytics Ltd
#     License: Apache License Version 2.0
# """


import time
import unittest
import unittest.mock as mock
from freezegun import freeze_time
from typing import Any
from requests import ConnectTimeout

from snowplow_tracker.emitters import Emitter, AsyncEmitter, DEFAULT_MAX_LENGTH


# helpers
def mocked_flush(*args: Any) -> None:
    pass


def mocked_send_events(*args: Any) -> None:
    pass


def mocked_http_success(*args: Any) -> bool:
    return True


def mocked_http_failure(*args: Any) -> bool:
    return False

def mocked_http_response_success(*args: Any) -> int:
    return 200

def mocked_http_response_failure(*args: Any) -> int:
    return 400

def mocked_http_response_failure_retry(*args: Any) -> int:
    return 500

class TestEmitters(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_init(self) -> None:
        e = Emitter('0.0.0.0')
        self.assertEqual(e.endpoint, 'https://0.0.0.0/com.snowplowanalytics.snowplow/tp2')
        self.assertEqual(e.method, 'post')
        self.assertEqual(e.batch_size, 10)
        self.assertEqual(e.event_store.event_buffer, [])
        self.assertIsNone(e.byte_limit)
        self.assertIsNone(e.bytes_queued)
        self.assertIsNone(e.on_success)
        self.assertIsNone(e.on_failure)
        self.assertFalse(e.timer.is_active())
        self.assertIsNone(e.request_timeout)

    def test_init_batch_size(self) -> None:
        e = Emitter('0.0.0.0', batch_size=10)
        self.assertEqual(e.batch_size, 10)

    def test_init_post(self) -> None:
        e = Emitter('0.0.0.0')
        self.assertEqual(e.batch_size, DEFAULT_MAX_LENGTH)

    def test_init_byte_limit(self) -> None:
        e = Emitter('0.0.0.0', byte_limit=512)
        self.assertEqual(e.bytes_queued, 0)

    def test_init_requests_timeout(self) -> None:
        e = Emitter('0.0.0.0', request_timeout=(2.5, 5))
        self.assertEqual(e.request_timeout, (2.5, 5))

    def test_as_collector_uri(self) -> None:
        uri = Emitter.as_collector_uri('0.0.0.0')
        self.assertEqual(uri, 'https://0.0.0.0/com.snowplowanalytics.snowplow/tp2')

    def test_as_collector_uri_get(self) -> None:
        uri = Emitter.as_collector_uri('0.0.0.0', method='get')
        self.assertEqual(uri, 'https://0.0.0.0/i')

    def test_as_collector_uri_port(self) -> None:
        uri = Emitter.as_collector_uri('0.0.0.0', port=9090)
        self.assertEqual(uri, 'https://0.0.0.0:9090/com.snowplowanalytics.snowplow/tp2')

    def test_as_collector_uri_http(self) -> None:
        uri = Emitter.as_collector_uri('0.0.0.0', protocol="http")
        self.assertEqual(uri, 'http://0.0.0.0/com.snowplowanalytics.snowplow/tp2')

    def test_as_collector_uri_empty_string(self) -> None:
        with self.assertRaises(ValueError):
            Emitter.as_collector_uri('')

    def test_as_collector_uri_endpoint_protocol(self) -> None:
        uri = Emitter.as_collector_uri("https://0.0.0.0")
        self.assertEqual(uri, "https://0.0.0.0/com.snowplowanalytics.snowplow/tp2")

    def test_as_collector_uri_endpoint_protocol_http(self) -> None:
        uri = Emitter.as_collector_uri("http://0.0.0.0")
        self.assertEqual(uri, "http://0.0.0.0/com.snowplowanalytics.snowplow/tp2")
        
    @mock.patch('snowplow_tracker.Emitter.flush')
    def test_input_no_flush(self, mok_flush: Any) -> None:
        mok_flush.side_effect = mocked_flush

        e = Emitter('0.0.0.0', method="get", batch_size=2)
        nvPairs = {"n0": "v0", "n1": "v1"}
        e.input(nvPairs)

        self.assertEqual(len(e.event_store.event_buffer), 1)
        self.assertDictEqual(nvPairs, e.event_store.event_buffer[0])
        self.assertIsNone(e.byte_limit)
        self.assertFalse(e.reached_limit())
        mok_flush.assert_not_called()

    @mock.patch('snowplow_tracker.Emitter.flush')
    def test_input_flush_byte_limit(self, mok_flush: Any) -> None:
        mok_flush.side_effect = mocked_flush

        e = Emitter('0.0.0.0', method="get", batch_size=2, byte_limit=16)
        nvPairs = {"n0": "v0", "n1": "v1"}
        e.input(nvPairs)

        self.assertEqual(len(e.event_store.event_buffer), 1)
        self.assertDictEqual(nvPairs, e.event_store.event_buffer[0])
        self.assertTrue(e.reached_limit())
        self.assertEqual(mok_flush.call_count, 1)

    @mock.patch('snowplow_tracker.Emitter.flush')
    def test_input_flush_buffer(self, mok_flush: Any) -> None:
        mok_flush.side_effect = mocked_flush

        e = Emitter('0.0.0.0', method="get", batch_size=2, byte_limit=1024)
        nvPairs = {"n0": "v0", "n1": "v1"}
        e.input(nvPairs)

        self.assertEqual(len(e.event_store.event_buffer), 1)
        self.assertFalse(e.reached_limit())
        self.assertDictEqual(nvPairs, e.event_store.event_buffer[0])

        nextPairs = {"n0": "v0"}
        e.input(nextPairs)
        # since we mock flush, the buffer is not empty
        self.assertEqual(e.event_store.event_buffer, [nvPairs, nextPairs])
        self.assertTrue(e.reached_limit())
        self.assertEqual(mok_flush.call_count, 1)

    @mock.patch('snowplow_tracker.Emitter.flush')
    def test_input_bytes_queued(self, mok_flush: Any) -> None:
        mok_flush.side_effect = mocked_flush

        e = Emitter('0.0.0.0', method="get", batch_size=2, byte_limit=1024)
        nvPairs = {"n0": "v0", "n1": "v1"}
        e.input(nvPairs)

        self.assertEqual(len(e.event_store.event_buffer), 1)
        self.assertEqual(e.bytes_queued, 24)

        e.input(nvPairs)
        self.assertEqual(e.bytes_queued, 48)

    @mock.patch('snowplow_tracker.Emitter.flush')
    def test_input_bytes_post(self, mok_flush: Any) -> None:
        mok_flush.side_effect = mocked_flush

        e = Emitter('0.0.0.0')
        nvPairs = {"testString": "test", "testNum": 2.72}
        e.input(nvPairs)

        self.assertEqual(e.event_store.event_buffer, [{"testString": "test", "testNum": "2.72"}])

    @mock.patch('snowplow_tracker.Emitter.http_post')
    def test_flush(self, mok_send_events: Any) -> None:
        mok_send_events.side_effect = mocked_http_response_success

        e = Emitter('0.0.0.0', batch_size=2, byte_limit=None)
        nvPairs = {"n": "v"}
        e.input(nvPairs)
        e.input(nvPairs)

        self.assertEqual(mok_send_events.call_count, 1)
        self.assertEqual(len(e.event_store.event_buffer), 0)

    @mock.patch('snowplow_tracker.Emitter.http_post')
    def test_flush_bytes_queued(self, mok_send_events: Any) -> None:
        mok_send_events.side_effect = mocked_http_response_success

        e = Emitter('0.0.0.0', batch_size=2, byte_limit=256)
        nvPairs = {"n": "v"}
        e.input(nvPairs)
        e.input(nvPairs)

        self.assertEqual(mok_send_events.call_count, 1)
        self.assertEqual(len(e.event_store.event_buffer), 0)
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

    @mock.patch('snowplow_tracker.Emitter.flush')
    def test_flush_timer(self, mok_flush: Any) -> None:
        mok_flush.side_effect = mocked_flush

        e = Emitter('0.0.0.0', batch_size=10)
        ev_list = [{"a": "aa"}, {"b": "bb"}, {"c": "cc"}]
        for i in ev_list:
            e.input(i)

        e.set_flush_timer(3)
        self.assertEqual(len(e.event_store.event_buffer), 3)
        time.sleep(5)
        self.assertGreaterEqual(mok_flush.call_count, 1)

    @mock.patch('snowplow_tracker.Emitter.http_get')
    def test_send_events_get_success(self, mok_http_get: Any) -> None:
        mok_http_get.side_effect = mocked_http_response_success
        mok_success = mock.Mock(return_value="success mocked")
        mok_failure = mock.Mock(return_value="failure mocked")

        e = Emitter('0.0.0.0', method="get", batch_size=10, on_success=mok_success, on_failure=mok_failure)

        evBuffer = [{"a": "aa"}, {"b": "bb"}, {"c": "cc"}]
        e.send_events(evBuffer)
        mok_success.assert_called_once_with(evBuffer)
        mok_failure.assert_not_called()

    @mock.patch('snowplow_tracker.Emitter.http_get')
    def test_send_events_get_failure(self, mok_http_get: Any) -> None:
        mok_http_get.side_effect = mocked_http_response_failure
        mok_success = mock.Mock(return_value="success mocked")
        mok_failure = mock.Mock(return_value="failure mocked")

        e = Emitter('0.0.0.0', method="get", batch_size=10, on_success=mok_success, on_failure=mok_failure)

        evBuffer = [{"a": "aa"}, {"b": "bb"}, {"c": "cc"}]
        e.send_events(evBuffer)
        mok_success.assert_not_called()
        mok_failure.assert_called_once_with(0, evBuffer)

    @mock.patch('snowplow_tracker.Emitter.http_post')
    def test_send_events_post_success(self, mok_http_post: Any) -> None:
        mok_http_post.side_effect = mocked_http_response_success
        mok_success = mock.Mock(return_value="success mocked")
        mok_failure = mock.Mock(return_value="failure mocked")

        e = Emitter('0.0.0.0', batch_size=10, on_success=mok_success, on_failure=mok_failure)

        evBuffer = [{"a": "aa"}, {"b": "bb"}, {"c": "cc"}]
        e.send_events(evBuffer)
        mok_success.assert_called_once_with(evBuffer)
        mok_failure.assert_not_called()

    @mock.patch('snowplow_tracker.Emitter.http_post')
    def test_send_events_post_failure(self, mok_http_post: Any) -> None:
        mok_http_post.side_effect = mocked_http_response_failure
        mok_success = mock.Mock(return_value="success mocked")
        mok_failure = mock.Mock(return_value="failure mocked")

        e = Emitter('0.0.0.0', batch_size=10, on_success=mok_success, on_failure=mok_failure)

        evBuffer = [{"a": "aa"}, {"b": "bb"}, {"c": "cc"}]
        e.send_events(evBuffer)
        mok_success.assert_not_called()
        mok_failure.assert_called_with(0, evBuffer)

    @mock.patch('snowplow_tracker.emitters.requests.post')
    def test_http_post_connect_timeout_error(self, mok_post_request: Any) -> None:
        mok_post_request.side_effect = ConnectTimeout
        e = Emitter('0.0.0.0')
        response = e.http_post("dummy_string")
        post_succeeded = Emitter.is_good_status_code(response)

        self.assertFalse(post_succeeded)

    @mock.patch('snowplow_tracker.emitters.requests.post')
    def test_http_get_connect_timeout_error(self, mok_post_request: Any) -> None:
        mok_post_request.side_effect = ConnectTimeout
        e = Emitter('0.0.0.0', method='get')
        response = e.http_get({"a": "b"})
        get_succeeded = Emitter.is_good_status_code(response)
        self.assertFalse(get_succeeded)

    ###
    # AsyncEmitter
    ###
    @mock.patch('snowplow_tracker.AsyncEmitter.flush')
    def test_async_emitter_input(self, mok_flush: Any) -> None:
        mok_flush.side_effect = mocked_flush

        ae = AsyncEmitter('0.0.0.0', port=9090, method="get", batch_size=3, thread_count=5)
        self.assertTrue(ae.queue.empty())

        ae.input({"a": "aa"})
        ae.input({"b": "bb"})
        self.assertEqual(len(ae.event_store.event_buffer), 2)
        self.assertTrue(ae.queue.empty())
        mok_flush.assert_not_called()

        ae.input({"c": "cc"})  # meet buffer size
        self.assertEqual(mok_flush.call_count, 1)

    @mock.patch('snowplow_tracker.AsyncEmitter.send_events')
    def test_async_emitter_sync_flash(self, mok_send_events: Any) -> None:
        mok_send_events.side_effect = mocked_send_events

        ae = AsyncEmitter('0.0.0.0', port=9090, method="get", batch_size=3, thread_count=5, byte_limit=1024)
        self.assertTrue(ae.queue.empty())

        ae.input({"a": "aa"})
        ae.input({"b": "bb"})
        self.assertEqual(len(ae.event_store.event_buffer), 2)
        self.assertTrue(ae.queue.empty())
        mok_send_events.assert_not_called()

        ae.sync_flush()
        self.assertEqual(len(ae.event_store.event_buffer), 0)
        self.assertEqual(ae.bytes_queued, 0)
        self.assertEqual(mok_send_events.call_count, 1)

    @mock.patch('snowplow_tracker.Emitter.http_get')
    def test_async_send_events_get_success(self, mok_http_get: Any) -> None:
        mok_http_get.side_effect = mocked_http_response_success
        mok_success = mock.Mock(return_value="success mocked")
        mok_failure = mock.Mock(return_value="failure mocked")

        ae = AsyncEmitter('0.0.0.0', method="get", batch_size=10, on_success=mok_success, on_failure=mok_failure)

        evBuffer = [{"a": "aa"}, {"b": "bb"}, {"c": "cc"}]
        ae.send_events(evBuffer)
        mok_success.assert_called_once_with(evBuffer)
        mok_failure.assert_not_called()

    @mock.patch('snowplow_tracker.Emitter.http_get')
    def test_async_send_events_get_failure(self, mok_http_get: Any) -> None:
        mok_http_get.side_effect = mocked_http_response_failure
        mok_success = mock.Mock(return_value="success mocked")
        mok_failure = mock.Mock(return_value="failure mocked")

        ae = AsyncEmitter('0.0.0.0', method="get", batch_size=10, on_success=mok_success, on_failure=mok_failure)

        evBuffer = [{"a": "aa"}, {"b": "bb"}, {"c": "cc"}]
        ae.send_events(evBuffer)
        mok_success.assert_not_called()
        mok_failure.assert_called_once_with(0, evBuffer)

    @mock.patch('snowplow_tracker.Emitter.http_post')
    def test_async_send_events_post_success(self, mok_http_post: Any) -> None:
        mok_http_post.side_effect = mocked_http_response_success
        mok_success = mock.Mock(return_value="success mocked")
        mok_failure = mock.Mock(return_value="failure mocked")

        ae = Emitter('0.0.0.0', batch_size=10, on_success=mok_success, on_failure=mok_failure)

        evBuffer = [{"a": "aa"}, {"b": "bb"}, {"c": "cc"}]
        ae.send_events(evBuffer)
        mok_success.assert_called_once_with(evBuffer)
        mok_failure.assert_not_called()

    @mock.patch('snowplow_tracker.Emitter.http_post')
    def test_async_send_events_post_failure(self, mok_http_post: Any) -> None:
        mok_http_post.side_effect = mocked_http_response_failure
        mok_success = mock.Mock(return_value="success mocked")
        mok_failure = mock.Mock(return_value="failure mocked")

        ae = Emitter('0.0.0.0', batch_size=10, on_success=mok_success, on_failure=mok_failure)

        evBuffer = [{"a": "aa"}, {"b": "bb"}, {"c": "cc"}]
        ae.send_events(evBuffer)
        mok_success.assert_not_called()
        mok_failure.assert_called_with(0, evBuffer)

    # Unicode
    @mock.patch('snowplow_tracker.AsyncEmitter.flush')
    def test_input_unicode_get(self, mok_flush: Any) -> None:
        mok_flush.side_effect = mocked_flush

        payload = {"unicode": u'\u0107', "alsoAscii": "abc"}
        ae = AsyncEmitter('0.0.0.0', method="get", batch_size=2)
        ae.input(payload)

        self.assertEqual(len(ae.event_store.event_buffer), 1)
        self.assertDictEqual(payload, ae.event_store.event_buffer[0])

    @mock.patch('snowplow_tracker.AsyncEmitter.flush')
    def test_input_unicode_post(self, mok_flush: Any) -> None:
        mok_flush.side_effect = mocked_flush

        payload = {"unicode": u'\u0107', "alsoAscii": "abc"}
        ae = AsyncEmitter('0.0.0.0', batch_size=2)
        ae.input(payload)

        self.assertEqual(len(ae.event_store.event_buffer), 1)
        self.assertDictEqual(payload, ae.event_store.event_buffer[0])

    @mock.patch('snowplow_tracker.Emitter.http_post')
    def test_send_events_post_retry(self, mok_http_post: Any) -> None:
        mok_http_post.side_effect = mocked_http_response_failure_retry
        mok_success = mock.Mock(return_value="success mocked")
        mok_failure = mock.Mock(return_value="failure mocked")

        e = Emitter('0.0.0.0', batch_size=10, on_success=mok_success, on_failure=mok_failure)
        evBuffer = [{"a": "aa"}, {"b": "bb"}, {"c": "cc"}]
        e.send_events(evBuffer)
        
        mok_http_post.side_effect = mocked_http_response_success
        time.sleep(5)

        mok_failure.assert_called_with(0, evBuffer)
        mok_success.assert_called_with(evBuffer)

    @mock.patch('snowplow_tracker.Emitter.http_get')
    def test_send_events_get_retry(self, mok_http_get: Any) -> None:
        mok_http_get.side_effect = mocked_http_response_failure_retry
        mok_success = mock.Mock(return_value="success mocked")
        mok_failure = mock.Mock(return_value="failure mocked")

        e = Emitter('0.0.0.0', method='get', batch_size=1, on_success=mok_success, on_failure=mok_failure)
        evBuffer = [{"a": "aa"}, {"b": "bb"}, {"c": "cc"}]
        e.send_events(evBuffer)
        
        mok_http_get.side_effect = mocked_http_response_success
        time.sleep(5)

        mok_failure.assert_called_with(0, evBuffer)
        mok_success.assert_called_with(evBuffer)

    @mock.patch('snowplow_tracker.Emitter.http_get')
    def test_send_events_get_no_retry(self, mok_http_get: Any) -> None:
        mok_http_get.side_effect = mocked_http_response_failure
        mok_success = mock.Mock(return_value="success mocked")
        mok_failure = mock.Mock(return_value="failure mocked")

        e = Emitter('0.0.0.0', method='get', batch_size=1, on_success=mok_success, on_failure=mok_failure)
        evBuffer = [{"a": "aa"}, {"b": "bb"}, {"c": "cc"}]
        e.send_events(evBuffer)
        
        mok_failure.assert_called_once_with(0, evBuffer)
        mok_success.assert_not_called()

    @mock.patch('snowplow_tracker.Emitter.http_post')
    def test_send_events_post_no_retry(self, mok_http_post: Any) -> None:
        mok_http_post.side_effect = mocked_http_response_failure
        mok_success = mock.Mock(return_value="success mocked")
        mok_failure = mock.Mock(return_value="failure mocked")

        e = Emitter('0.0.0.0', method='get', batch_size=1, on_success=mok_success, on_failure=mok_failure)
        evBuffer = [{"a": "aa"}, {"b": "bb"}, {"c": "cc"}]
        e.send_events(evBuffer)
        
        mok_failure.assert_called_once_with(0, evBuffer)
        mok_success.assert_not_called()

    @mock.patch('snowplow_tracker.Emitter.http_post')
    def test_send_events_post_custom_retry(self, mok_http_post: Any) -> None:
        mok_http_post.side_effect = mocked_http_response_failure
        mok_success = mock.Mock(return_value="success mocked")
        mok_failure = mock.Mock(return_value="failure mocked")

        e = Emitter('0.0.0.0', batch_size=10, on_success=mok_success, on_failure=mok_failure, custom_retry_codes={400: True})
        evBuffer = [{"a": "aa"}, {"b": "bb"}, {"c": "cc"}]
        e.send_events(evBuffer)
        
        mok_http_post.side_effect = mocked_http_response_success
        time.sleep(5)

        mok_failure.assert_called_with(0, evBuffer)
        mok_success.assert_called_with(evBuffer)

    @mock.patch('snowplow_tracker.Emitter.http_get')
    def test_send_events_get_custom_retry(self, mok_http_get: Any) -> None:
        mok_http_get.side_effect = mocked_http_response_failure
        mok_success = mock.Mock(return_value="success mocked")
        mok_failure = mock.Mock(return_value="failure mocked")

        e = Emitter('0.0.0.0', method='get',batch_size=10, on_success=mok_success, on_failure=mok_failure, custom_retry_codes={400: True})
        evBuffer = [{"a": "aa"}, {"b": "bb"}, {"c": "cc"}]
        e.send_events(evBuffer)
        
        mok_http_get.side_effect = mocked_http_response_success
        time.sleep(5)

        mok_failure.assert_called_with(0, evBuffer)
        mok_success.assert_called_with(evBuffer)

