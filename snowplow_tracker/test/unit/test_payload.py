"""
    test_payload.py

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
from freezegun import freeze_time
from snowplow_tracker import payload


def is_subset(dict1, dict2):
    """
    * is_subset(smaller_dict, larger_dict)
        Checks if dict1 has name, value pairs that also exist in dict2.
        Typically this function is used in the case where dict1 (expected
        output) contains certain name, value pairs, and those have to be
        compared with name, value pairs in another dict (the actual output)
    """
    if len(dict1) > len(dict2):
        return False
    if set(dict1.items()).issubset(dict2.items()):
        return True
    else:
        return False


class TestPayload(unittest.TestCase):

    def setUp(self):
        pass

    def test_object_generation(self):
        p = payload.Payload()
        self.assertTrue(is_subset({}, p.context))

    def test_object_generation_2(self):
        p = payload.Payload(None, {"test1": "result1", "test2": "result2", })
        output = {"test1": "result1", "test2": "result2"}
        self.assertTrue(is_subset(output, p.context))

    def test_add(self):
        p = payload.Payload()
        p.add("name1", "value1")
        p.add("name2", "value2")
        output = {"name1": "value1", "name2": "value2", }
        self.assertTrue(is_subset(output, p.context))

    def test_add_dict(self):
        p = payload.Payload(None, {"n1": "v1", "n2": "v2", })
        p.add_dict({"name4": 4, "name3": 3})            # Order doesn't matter
        output = {"n1": "v1", "n2": "v2", "name3": 3, "name4": 4}
        self.assertTrue(is_subset(output, p.context))

    def test_get_transaction_id(self):
        p = payload.Payload()
        self.assertTrue(p.context["tid"] >= 100000 and
                        p.context["tid"] <= 999999)

    @freeze_time("1970-01-01 00:00:01")
    def test_get_timestamp(self):
        p = payload.Payload()
        self.assertEquals(p.context["dtm"], 1000)   # 1970-01-01 00:00:01 in ms

    def test_set_timestamp_2(self):
        p = payload.Payload()
        p.set_timestamp(0)
        self.assertEquals(p.context["dtm"], 0)

    def test_set_timestamp(self):
        p = payload.Payload()
        p.set_timestamp(12345654321)
        self.assertEquals(p.context["dtm"], 12345654321000)

    def test_add_unstruct_1(self):
        p = payload.Payload()
        try:
            p.add_unstruct({"product_id": "ASO01043",
                        "price$flt": 33,                 # ERROR
                        "walrus$tms": int(time.time() * 1000),
                       }, False, "ue_px", "ue_pe")
        except RuntimeError as e:
            self.assertEquals("price$flt in dict is not a flt", str(e))

    def test_add_unstruct_2(self):
        p = payload.Payload()
        try:
            p.add_unstruct({"product_id": "ASO01043",
                        "price$flt": 33.3,
                        "walrus$tms": "hello world!",   # ERROR
                       }, True, "ue_px", "ue_pe")
        except RuntimeError as e:
            self.assertEquals("walrus$tms in dict is not a tms", str(e))
