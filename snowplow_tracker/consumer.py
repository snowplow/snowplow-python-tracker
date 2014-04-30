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
import redis

DEFAULT_MAX_LENGTH = 10
HTTP_ERRORS = {"host not found",
               "No address associated with name",
               "No address associated with hostname"}


class Consumer(object):

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def input(self, payload):

        """
            Send a GET request to the collector URI (generated from the
            new_tracker methods) and return the relevant error message if any.

            :param  payload:        Generated dict track()
            :type   payload:        payload
            :rtype:                 tuple(bool, int | str)
        """

        r = requests.get(self.endpoint, params=payload)
        code = r.status_code
        if code in HTTP_ERRORS:
            return (False, "Host [" + r.url + "] not found (possible connectivity error)")
        elif code < 0 or code >= 400:
            return (False, code)
        else:
            return (True, code+99)


class AsyncConsumer(Consumer):

    def __init__(self, endpoint):
        super(AsyncConsumer, self).__init__(endpoint)

    def input(self, payload):

        t = threading.Thread(target=super(AsyncConsumer, self).input, args=[payload])
        t.start()


class BufferedConsumer(object):

    def __init__(self, endpoint, max_length=DEFAULT_MAX_LENGTH):

        self.endpoint = endpoint
        self.max_length = max_length
        self.queue = []

    def input(self, payload):

        self.queue.append(payload)
        if len(self.queue) >= self.max_length:
            self.flush()

    def flush(self):
        
        batch = json.dumps(self.queue)
        self.queue = []
        r = requests.post(self.endpoint, data=batch);


class AsyncBufferedConsumer(BufferedConsumer):

    def __init(self, endpoint, max_length=DEFAULT_MAX_LENGTH):
        super(AsyncBufferedConsumer, self).__init__(endpoint, max_length)

    def flush(self):

        t = threading.Thread(target=super(AsyncBufferedConsumer, self).flush)
        t.start()


class RedisConsumer(object):

    def __init__(self, key, host="localhost", port=6379, db=9):
        self.rdb = redis.StrictRedis(host, port, db)

    def input(self, payload):
        self.rdb.rpush(key, json.dumps(payload))
