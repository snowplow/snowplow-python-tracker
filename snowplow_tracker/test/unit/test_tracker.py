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


import unittest
from freezegun import freeze_time
from snowplow_tracker.tracker import Tracker
from snowplow_tracker.consumer import Consumer


class TestTracker(unittest.TestCase):

    def setUp(self):
        pass

    def test_initialisation(self):
        t = Tracker(Consumer("d3rkrsqld9gmqf.cloudfront.net"), namespace="cloudfront", encode_base64= False, app_id="AF003", context_vendor="com.example")
        self.assertEquals(t.standard_nv_pairs["tna"], "cloudfront")
        self.assertEquals(t.standard_nv_pairs["aid"], "AF003")
        self.assertEquals(t.encode_base64, False)
        self.assertEquals(t.context_vendor, "com.example")

    def test_get_transaction_id(self):
        tid = Tracker.get_transaction_id()
        self.assertTrue(tid >= 100000 and tid <= 999999)

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
