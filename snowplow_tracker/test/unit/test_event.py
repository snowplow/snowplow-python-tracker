# """
#     test_event.py

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
# """

import json
import unittest
from snowplow_tracker.events import Event
from snowplow_tracker.subject import Subject
from snowplow_tracker.self_describing_json import SelfDescribingJson

CONTEXT_SCHEMA = "iglu:com.snowplowanalytics.snowplow/contexts/jsonschema/1-0-1"


class TestEvent(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_init(self):
        event = Event()
        self.assertEqual(event.payload.nv_pairs, {})

    def test_build_payload(self):
        event_subject = Subject()
        event = Event(event_subject=event_subject)
        payload = event.build_payload(encode_base64=None, json_encoder=None)

        self.assertEqual(payload.nv_pairs, {"p": "pc"})

    def test_build_payload_tstamp(self):
        event_subject = Subject()
        tstamp = 1399021242030

        event = Event(event_subject=event_subject, true_timestamp=tstamp)

        payload = event.build_payload(
            json_encoder=None,
            encode_base64=None,
        )

        self.assertEqual(payload.nv_pairs, {"p": "pc", "ttm": 1399021242030})

    def test_build_payload_context(self):
        event_subject = Subject()
        context = SelfDescribingJson("test.context.schema", {"user": "tester"})
        event_context = [context]
        event = Event(event_subject=event_subject, context=event_context)

        payload = event.build_payload(
            json_encoder=None,
            encode_base64=False,
        )

        expected_context = {
            "schema": CONTEXT_SCHEMA,
            "data": [{"schema": "test.context.schema", "data": {"user": "tester"}}],
        }
        actual_context = json.loads(payload.nv_pairs["co"])

        self.assertDictEqual(actual_context, expected_context)
