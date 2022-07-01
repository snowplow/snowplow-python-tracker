"""
    test_payload.py

    Copyright (c) 2013-2022 Snowplow Analytics Ltd. All rights reserved.

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
    Copyright: Copyright (c) 2013-2022 Snowplow Analytics Ltd
    License: Apache License Version 2.0
"""

import json
import base64
import unittest
from typing import Dict, Any

from snowplow_tracker import payload


def is_subset(dict1: Dict[Any, Any], dict2: Dict[Any, Any]) -> bool:
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


def date_encoder(o: Any) -> str:
    """Sample custom JSON encoder which converts dates into their ISO format"""
    from datetime import date
    from json.encoder import JSONEncoder

    if isinstance(o, date):
        return o.isoformat()

    return JSONEncoder.default(o)


class TestPayload(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_object_generation(self) -> None:
        p = payload.Payload()
        self.assertDictEqual({}, p.nv_pairs)

    def test_object_generation_2(self) -> None:
        p = payload.Payload({"test1": "result1", "test2": "result2", })
        output = {"test1": "result1", "test2": "result2"}
        self.assertDictEqual(output, p.nv_pairs)

    def test_add(self) -> None:
        p = payload.Payload()
        p.add("name1", "value1")
        p.add("name2", "value2")
        output = {"name1": "value1", "name2": "value2", }
        self.assertDictEqual(output, p.nv_pairs)

    def test_add_empty_val(self) -> None:
        p = payload.Payload()
        p.add("name", "")
        output = {}
        self.assertDictEqual(output, p.nv_pairs)

    def test_add_none(self) -> None:
        p = payload.Payload()
        p.add("name", None)
        output = {}
        self.assertDictEqual(output, p.nv_pairs)

    def test_add_dict(self) -> None:
        p = payload.Payload({"n1": "v1", "n2": "v2", })
        p.add_dict({"name4": 4, "name3": 3})            # Order doesn't matter
        output = {"n1": "v1", "n2": "v2", "name3": 3, "name4": 4}
        self.assertDictEqual(output, p.nv_pairs)

    def test_add_json_empty(self) -> None:
        p = payload.Payload({'name': 'value'})
        input = {}
        p.add_json(input, False, 'ue_px', 'ue_pr')
        output = {'name': 'value'}
        self.assertDictEqual(output, p.nv_pairs)

    def test_add_json_none(self) -> None:
        p = payload.Payload({'name': 'value'})
        input = None
        p.add_json(input, False, 'ue_px', 'ue_pr')
        output = {'name': 'value'}
        self.assertDictEqual(output, p.nv_pairs)

    def test_add_json_encode_false(self) -> None:
        p = payload.Payload()
        input = {'a': 1}
        p.add_json(input, False, 'ue_px', 'ue_pr')
        self.assertTrue('ue_pr' in p.nv_pairs.keys())
        self.assertFalse('ue_px' in p.nv_pairs.keys())

    def test_add_json_encode_true(self) -> None:
        p = payload.Payload()
        input = {'a': 1}
        p.add_json(input, True, 'ue_px', 'ue_pr')
        self.assertFalse('ue_pr' in p.nv_pairs.keys())
        self.assertTrue('ue_px' in p.nv_pairs.keys())

    def test_add_json_unicode_encode_false(self) -> None:
        p = payload.Payload()
        input = {'a': u'\u0107', u'\u0107': 'b'}
        p.add_json(input, False, 'ue_px', 'ue_pr')
        ue_pr = json.loads(p.nv_pairs["ue_pr"])
        self.assertDictEqual(input, ue_pr)

    def test_add_json_unicode_encode_true(self) -> None:
        p = payload.Payload()
        input = {'a': '\u0107', '\u0107': 'b'}
        p.add_json(input, True, 'ue_px', 'ue_pr')
        ue_px = json.loads(base64.urlsafe_b64decode(p.nv_pairs["ue_px"]).decode('utf-8'))
        self.assertDictEqual(input, ue_px)

    def test_add_json_with_custom_enc(self) -> None:
        from datetime import date

        p = payload.Payload()

        input = {"key1": date(2020, 2, 1)}

        p.add_json(input, False, "name1", "name1", date_encoder)

        results = json.loads(p.nv_pairs["name1"])
        self.assertTrue(is_subset({"key1": "2020-02-01"}, results))

    def test_subject_get(self) -> None:
        p = payload.Payload({'name1': 'val1'})
        self.assertDictEqual(p.get(), p.nv_pairs)
