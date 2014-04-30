"""
    redis_worke.py

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


import redis
import gevent
from gevent.pool import Pool
from consumer import Consumer
import json
import signal

DEFAULT_REDIS = redis.StrictRedis()
DEFAULT_KEY = "snowplow"

class RedisWorker(object):

    def __init__(self, _consumer, key=DEFAULT_KEY, dbr=DEFAULT_REDIS):
        self.key = key
        self.dbr = dbr
        self.consumer = _consumer
        self.pool = Pool(5)

    def send(self, payload):
        self.consumer.input(payload)

    def pop_payload(self):
        payload = self.dbr.lpop(self.key)
        if payload:
            self.pool.spawn(self.send, json.loads(payload))
        else:
            gevent.sleep(5)

    def run(self):
        self._shutdown = False

        while not self._shutdown:
            self.pop_payload()
        self.pool.join(timeout=20)

    def request_shutdown(self):
        self._shutdown = True
