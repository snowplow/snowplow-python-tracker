"""
    test_tracker.py

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


import re
import time
import unittest

from contracts.interface import ContractNotRespected
from freezegun import freeze_time

from snowplow_tracker.tracker import Tracker
from snowplow_tracker.emitters import Emitter


class TestTracker(unittest.TestCase):

    def setUp(self):
        pass

    def test_initialisation(self):
        t = Tracker([Emitter("d3rkrsqld9gmqf.cloudfront.net")], namespace="cloudfront", encode_base64= False, app_id="AF003")
        self.assertEquals(t.standard_nv_pairs["tna"], "cloudfront")
        self.assertEquals(t.standard_nv_pairs["aid"], "AF003")
        self.assertEquals(t.encode_base64, False)

    def test_get_uuid(self):
        eid = Tracker.get_uuid()
        self.assertIsNotNone(re.match('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z', eid))

    @freeze_time("1970-01-01 00:00:01")
    def test_get_timestamp(self):
        dtm = Tracker.get_timestamp()
        self.assertEquals(dtm, 1000)   # 1970-01-01 00:00:01 in ms

    def test_set_timestamp_1(self):
        dtm = Tracker.get_timestamp(1399021242030)
        self.assertEquals(dtm, 1399021242030)

    def test_set_timestamp_2(self):
        dtm = Tracker.get_timestamp(1399021242240.0303)
        self.assertEquals(dtm, 1399021242240)

    def test_add_emitter(self):
        e1 = Emitter("d3rkrsqld9gmqf.cloudfront.net", method="get")
        e2 = Emitter("d3rkrsqld9gmqf.cloudfront.net", method="post")
        t = Tracker(e1, namespace="cloudfront", encode_base64=False, app_id="AF003")
        t.add_emitter(e2)
        self.assertEquals(t.emitters, [e1, e2])

    def test_alias_contract(self):
        e1 = Emitter("d3rkrsqld9gmqf.cloudfront.net", method="get")
        t = Tracker(e1, namespace="cloudfront", encode_base64=False, app_id="AF003")
        try:
            t.track_self_describing_event("not-SelfDescribingJson")
        except Exception as e:
            self.assertIsInstance(e, ContractNotRespected)

    def test_flush_timer(self):
        e1 = Emitter("d3rkrsqld9gmqf.cloudfront.net", method="post", buffer_size=10)
        t = Tracker(e1, namespace="cloudfront", encode_base64=False, app_id="AF003")
        e1.set_flush_timer(3)
        t.track_page_view("http://snowplowanalytics.com/blog/2016/09/22/introducing-sauna-a-decisioning-and-response-platform/")
        t.track_page_view("http://snowplowanalytics.com/blog/2016/03/17/2015-2016-winternship-wrapup/")
        t.track_page_view("http://snowplowanalytics.com/blog/2016/07/31/iglu-r5-scinde-dawk-released/")
        self.assertEqual(len(e1.buffer), 3)
        time.sleep(4)
        self.assertEqual(len(e1.buffer), 0)
        t.track_page_view("http://snowplowanalytics.com/blog/2016/03/03/guide-to-debugging-bad-data-in-elasticsearch-kibana/")
        t.track_page_view("http://snowplowanalytics.com/blog/2016/03/17/2015-2016-winternship-wrapup/")
        self.assertEqual(len(e1.buffer), 2)


