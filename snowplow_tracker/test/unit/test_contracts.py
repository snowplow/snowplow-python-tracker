"""
    test_tracker.py

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

import unittest

from snowplow_tracker.contracts import form_element, greater_than, non_empty, non_empty_string, one_of, satisfies


class TestContracts(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_greater_than_succeeds(self) -> None:
        greater_than(10, 0)

    def test_greater_than_fails(self) -> None:
        with self.assertRaises(ValueError):
            greater_than(0, 10)

    def test_non_empty_succeeds(self) -> None:
        non_empty(['something'])

    def test_non_empty_fails(self) -> None:
        with self.assertRaises(ValueError):
            non_empty([])

    def test_non_empty_string_succeeds(self) -> None:
        non_empty_string('something')

    def test_non_empty_string_fails(self) -> None:
        with self.assertRaises(ValueError):
            non_empty_string('')

    def test_one_of_succeeds(self) -> None:
        one_of('something', ['something', 'something else'])

    def test_one_of_fails(self) -> None:
        with self.assertRaises(ValueError):
            one_of('something', ['something else'])

    def test_satisfies_succeeds(self) -> None:
        satisfies(10, lambda v: v == 10)

    def test_satisfies_fails(self) -> None:
        with self.assertRaises(ValueError):
            satisfies(0, lambda v: v == 10)

    def test_form_element_no_type(self) -> None:
        elem = {
            "name": "elemName",
            "value": "elemValue",
            "nodeName": "INPUT"
        }
        form_element(elem)

    def test_form_element_type_valid(self) -> None:
        elem = {
            "name": "elemName",
            "value": "elemValue",
            "nodeName": "TEXTAREA",
            "type": "button"
        }
        form_element(elem)

    def test_form_element_type_invalid(self) -> None:
        elem = {
            "name": "elemName",
            "value": "elemValue",
            "nodeName": "SELECT",
            "type": "invalid"
        }
        with self.assertRaises(ValueError):
            form_element(elem)

    def test_form_element_nodename_invalid(self) -> None:
        elem = {
            "name": "elemName",
            "value": "elemValue",
            "nodeName": "invalid"
        }
        with self.assertRaises(ValueError):
            form_element(elem)

    def test_form_element_no_nodename(self) -> None:
        elem = {
            "name": "elemName",
            "value": "elemValue"
        }
        with self.assertRaises(ValueError):
            form_element(elem)

    def test_form_element_no_value(self) -> None:
        elem = {
            "name": "elemName",
            "nodeName": "INPUT"
        }
        with self.assertRaises(ValueError):
            form_element(elem)

    def test_form_element_no_name(self) -> None:
        elem = {
            "value": "elemValue",
            "nodeName": "INPUT"
        }
        with self.assertRaises(ValueError):
            form_element(elem)
