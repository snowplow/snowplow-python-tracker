# """
#     test_in_memory_event_store.py

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

import unittest
from snowplow_tracker.event_store import InMemoryEventStore
import logging

# logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TestInMemoryEventStore(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_init(self):
        event_store = InMemoryEventStore(logger)
        self.assertEqual(event_store.buffer_capacity, 10000)
        self.assertEqual(event_store.event_buffer, [])

    def test_add_event(self):
        event_store = InMemoryEventStore(logger)
        nvPairs = {"n0": "v0", "n1": "v1"}

        event_store.add_event(nvPairs)
        self.assertDictEqual(nvPairs, event_store.event_buffer[0])

    def test_size(self):
        event_store = InMemoryEventStore(logger)
        nvPairs = {"n0": "v0", "n1": "v1"}

        event_store.add_event(nvPairs)
        event_store.add_event(nvPairs)
        event_store.add_event(nvPairs)

        self.assertEqual(event_store.size(), 3)

    def test_add_failed_events_to_buffer(self):
        event_store = InMemoryEventStore(logger)

        nvPair1 = {"n0": "v0", "n1": "v1"}
        nvPair2 = {"n2": "v2", "n3": "v3"}

        event_store.add_event(nvPair1)
        event_store.add_event(nvPair2)

        payload_list = event_store.get_events_batch()

        event_store.cleanup(payload_list, True)

        self.assertEqual(event_store.event_buffer, payload_list)

    def test_remove_success_events_from_buffer(self):
        event_store = InMemoryEventStore(logger)

        nvPairs = {"n0": "v0", "n1": "v1"}

        event_store.add_event(nvPairs)
        event_store.add_event(nvPairs)
        payload_list = event_store.get_events_batch()
        event_store.cleanup(payload_list, False)

        self.assertEqual(event_store.event_buffer, [])

    def test_drop_new_events_buffer_full(self):
        event_store = InMemoryEventStore(logger, buffer_capacity=2)

        nvPair1 = {"n0": "v0"}
        nvPair2 = {"n1": "v1"}
        nvPair3 = {"n2": "v2"}

        event_store.add_event(nvPair1)
        event_store.add_event(nvPair2)

        self.assertEqual(event_store.event_buffer, [{"n0": "v0"}, {"n1": "v1"}])

        event_store.add_event(nvPair3)

        self.assertEqual(event_store.event_buffer, [{"n0": "v0"}, {"n1": "v1"}])

    def test_get_events(self):
        event_store = InMemoryEventStore(logger, buffer_capacity=2)

        nvPairs = {"n0": "v0"}
        batch = [nvPairs, nvPairs]

        event_store.add_event(nvPairs)
        event_store.add_event(nvPairs)

        self.assertEqual(event_store.get_events_batch(), batch)
