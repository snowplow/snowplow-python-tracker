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
        self.assertTrue(is_subset({}, p.nv_pairs))

    def test_object_generation_2(self):
        p = payload.Payload({"test1": "result1", "test2": "result2", })
        output = {"test1": "result1", "test2": "result2"}
        self.assertTrue(is_subset(output, p.nv_pairs))

    def test_add(self):
        p = payload.Payload()
        p.add("name1", "value1")
        p.add("name2", "value2")
        output = {"name1": "value1", "name2": "value2", }
        self.assertTrue(is_subset(output, p.nv_pairs))

    def test_add_dict(self):
        p = payload.Payload({"n1": "v1", "n2": "v2", })
        p.add_dict({"name4": 4, "name3": 3})            # Order doesn't matter
        output = {"n1": "v1", "n2": "v2", "name3": 3, "name4": 4}
        self.assertTrue(is_subset(output, p.nv_pairs))
