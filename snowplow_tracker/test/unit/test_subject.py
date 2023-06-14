# """
#     test_subject.py

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
import pytest

from snowplow_tracker import subject as _subject


class TestSubject(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_subject_0(self) -> None:
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
        s.set_domain_session_id("domain-session-id")
        s.set_domain_session_index(1)
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
            "sid": "domain-session-id",
            "vid": 1,
            "tnuid": "network-user-id",
        }
        self.assertDictEqual(s.standard_nv_pairs, exp)

    def test_subject_1(self) -> None:
        s = _subject.Subject().set_platform("srv").set_user_id("1234").set_lang("EN")

        exp = {"p": "srv", "uid": "1234", "lang": "EN"}
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
            s.standard_nv_pairs["sid"]
        with pytest.raises(KeyError):
            s.standard_nv_pairs["vid"]
        with pytest.raises(KeyError):
            s.standard_nv_pairs["tnuid"]

    def test_combine_subject(self) -> None:
        s = _subject.Subject()
        s.set_color_depth(10)
        s.set_domain_session_id("domain_session_id")

        s2 = _subject.Subject()
        s2.set_domain_user_id("domain_user_id")
        s2.set_lang("en")

        fin_payload_dict = s.combine_subject(s2)

        expected_fin_payload_dict = {
            "p": "pc",
            "cd": 10,
            "sid": "domain_session_id",
            "duid": "domain_user_id",
            "lang": "en",
        }

        expected_subject = {
            "p": "pc",
            "cd": 10,
            "sid": "domain_session_id",
        }

        self.assertDictEqual(fin_payload_dict, expected_fin_payload_dict)
        self.assertDictEqual(s.standard_nv_pairs, expected_subject)
