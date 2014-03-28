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

    Authors: Anuj More, Alex Dean
    Copyright: Copyright (c) 2013-2014 Snowplow Analytics Ltd
    License: Apache License Version 2.0
"""


import unittest
from snowplow_tracker.tracker import Tracker


class TestTracker(unittest.TestCase):

    def setUp(self):
        pass

    """
    Testing URI generators
    """

    def test_as_collector_uri(self):
        host = "hello.snowplow.com"
        output = Tracker.as_collector_uri(host)
        exp_output = ''.join(["http://", host, "/i"])
        self.assertEquals(output, exp_output)

    def test_collector_uri_from_cf(self):
        cf_subdomain = "d3rkrsqld9gmqf"
        output = Tracker.collector_uri_from_cf(cf_subdomain)
        exp_output = ''.join(["http://", cf_subdomain, ".cloudfront.net/i"])
        self.assertEquals(output, exp_output)

    def test_new_tracker_for_uri(self):
        host = "hello.snowplow.com"
        output = Tracker.new_tracker_for_uri(host)
        exp_output = ''.join(["http://", host, "/i"])
        self.assertEquals(output, exp_output)

    def test_new_tracker_for_cf(self):
        cf_subdomain = "d3rkrsqld9gmqf"
        output = Tracker.new_tracker_for_cf(cf_subdomain)
        exp_output = ''.join(["http://", cf_subdomain, ".cloudfront.net/i"])
        self.assertEquals(output, exp_output)

    """
    Testing class methods
    """

    def test_cloudfront(self):
        cf_subdomain = "abc"
        output = Tracker.cloudfront(cf_subdomain)
        self.assertEquals(output.collector_uri, Tracker.new_tracker_for_cf(
                          cf_subdomain))

    def test_hostname(self):
        host = "walrus.snowplow.com"
        output = Tracker.hostname(host)
        self.assertEquals(output.collector_uri, Tracker.new_tracker_for_uri(
                          host))