"""
    consumer.py

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

import requests
import json
import threading
import celery
from celery.contrib.methods import task
import redis
import logging

app = celery.Celery('tasks', broker='redis://guest@localhost//')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DEFAULT_MAX_LENGTH = 10
HTTP_ERRORS = {"host not found",
               "No address associated with name",
               "No address associated with hostname"}

class Consumer(object):

    def __init__(self, endpoint, method="http-get", buffer_size=None):

        self.endpoint = self.as_collector_uri(endpoint)

        if buffer_size is None:
            if method == "http-post":
                buffer_size = DEFAULT_MAX_LENGTH
            else:
                buffer_size = 1
        self.buffer_size = buffer_size
        self.buffer = []

        self.method = method

    def as_collector_uri(self, endpoint):
        return "http://" + endpoint + "/i"

    def input(self, payload):
        self.buffer.append(payload)
        if len(self.buffer) >= self.buffer_size:
            self.flush()

    @task
    def flush(self):
        if self.method == "http-post":
            data = json.dumps(self.buffer)
            self.buffer = []
            self.http_post(data)

        elif self.method == "http-get":
            while len(self.buffer) > 0:
                payload = self.buffer.pop()
                self.http_get(payload)

    def http_post(self, data):
        r = requests.post(self.endpoint, data=data)

    def http_get(self, payload):
        r = requests.get(self.endpoint, params=payload)        

    def sync_flush(self):
        Consumer.flush(self)

class AsyncConsumer(Consumer):

    def flush(self):
        threading.Thread(target=super(AsyncConsumer, self).flush).start()

class CeleryConsumer(Consumer):

    def flush(self):
        super(CeleryConsumer, self).flush.delay()

class RedisConsumer(object):
    def __init__(self, rdb=None, key="snowplow"):
        if rdb is None:
            rdb = redis.StrictRedis()
        self.rdb = rdb
        self.key = key

    def input(self, payload):
        self.rdb.rpush(self.key, json.dumps(payload))

    def flush(self):
        pass
