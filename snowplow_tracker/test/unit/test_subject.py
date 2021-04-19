"""
    test_subject.py

    Copyright (c) 2013-2021 Snowplow Analytics Ltd. All rights reserved.

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
    Copyright: Copyright (c) 2013-2021 Snowplow Analytics Ltd
    License: Apache License Version 2.0
"""


import unittest
import pytest

from contracts.interface import ContractNotRespected

from snowplow_tracker import subject as _subject

class TestSubject(unittest.TestCase):

    def setUp(self):
        pass

    def test_subject_0(self):
        s = _subject.Subject()
        self.assertDictEqual(s.standard_nv_pairs, {"p": _subject.DEFAULT_PLATFORM})

        s.set_platform("srv")
        s.set_user_id("1234")
        s.set_screen_resolution(1920, 1080)
        s.set_viewport(1080, 1080)
        s.set_color_depth(1080)
        s.set_timezone("PST")
        s.set_lang("EN")
        s.set_domain_user_id("domain-user-id")
        s.set_ip_address("127.0.0.1")
        s.set_useragent("useragent-string")
        s.set_network_user_id("network-user-id")

        exp = {
            "p": "srv",
            "uid": "1234",
            "res": "1920x1080",
            "vp": "1080x1080",
            "cd": 1080,
            "tz": "PST",
            "lang": "EN",
            "ip": "127.0.0.1",
            "ua": "useragent-string",
            "duid": "domain-user-id",
            "tnuid": "network-user-id"
        }
        self.assertDictEqual(s.standard_nv_pairs, exp)

    def test_subject_1(self):
        s = _subject.Subject().set_platform("srv").set_user_id("1234").set_lang("EN")

        exp = {
            "p": "srv",
            "uid": "1234",
            "lang": "EN"
        }
        self.assertDictEqual(s.standard_nv_pairs, exp)

        with pytest.raises(KeyError):
            s.standard_nv_pairs["res"]
        with pytest.raises(KeyError):
            s.standard_nv_pairs["vp"]
        with pytest.raises(KeyError):
            s.standard_nv_pairs["cd"]
        with pytest.raises(KeyError):
            s.standard_nv_pairs["tz"]
        with pytest.raises(KeyError):
            s.standard_nv_pairs["ip"]
        with pytest.raises(KeyError):
            s.standard_nv_pairs["ua"]
        with pytest.raises(KeyError):
            s.standard_nv_pairs["duid"]
        with pytest.raises(KeyError):
            s.standard_nv_pairs["tnuid"]
