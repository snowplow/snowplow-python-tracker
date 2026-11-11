# """
#     test_self_describing_json.py
#
#     Copyright (c) 2026 Snowplow Analytics Ltd. All rights reserved.
#
#     This program is licensed to you under the Apache License Version 2.0,
#     and you may not use this file except in compliance with the Apache License
#     Version 2.0. You may obtain a copy of the Apache License Version 2.0 at
#     http://www.apache.org/licenses/LICENSE-2.0.
#
#     Unless required by applicable law or agreed to in writing,
#     software distributed under the Apache License Version 2.0 is distributed on
#     an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#     express or implied. See the Apache License Version 2.0 for the specific
#     language governing permissions and limitations there under.
# """

import json
import unittest
from decimal import Decimal

from snowplow_tracker import SelfDescribingJson


class TestSelfDescribingJson(unittest.TestCase):
    def test_to_string_default(self):
        event = SelfDescribingJson("test.schema", {"name": "caf\u00e9"})
        self.assertEqual(
            event.to_string(),
            '{"schema": "test.schema", "data": {"name": "caf\\u00e9"}}',
        )

    def test_to_string_formatting(self):
        event = SelfDescribingJson("test.schema", {"name": "caf\u00e9"})
        self.assertEqual(
            event.to_string(indent=2, sort_keys=True, ensure_ascii=False),
            '{\n  "data": {\n    "name": "caf\u00e9"\n  },\n'
            '  "schema": "test.schema"\n}',
        )

    def test_to_string_list_data(self):
        event = SelfDescribingJson("test.schema", [{"value": 1}])
        self.assertEqual(
            event.to_string(separators=(",", ":")),
            '{"schema":"test.schema","data":[{"value":1}]}',
        )

    def test_to_string_custom_encoder(self):
        class DecimalEncoder(json.JSONEncoder):
            def default(self, value):
                if isinstance(value, Decimal):
                    return str(value)
                return super().default(value)

        event = SelfDescribingJson("test.schema", {"price": Decimal("1.25")})
        self.assertEqual(
            json.loads(event.to_string(cls=DecimalEncoder))["data"],
            {"price": "1.25"},
        )
        with self.assertRaises(TypeError):
            event.to_string()

    def test_to_string_invalid_option(self):
        event = SelfDescribingJson("test.schema", {})
        with self.assertRaises(TypeError):
            event.to_string(unknown_option=True)
