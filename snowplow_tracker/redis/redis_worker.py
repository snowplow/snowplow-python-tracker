"""
    redis_worker.py

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


import json
import signal

_REDIS_OPT = True
try:
    import redis
    import gevent
    from gevent.pool import Pool
except ImportError:
    _REDIS_OPT = False


DEFAULT_KEY = "snowplow"

class RedisWorker(object):
    """
        Asynchronously take events from redis and send them to an emitter
    """
    if _REDIS_OPT:

        def __init__(self, emitter, rdb=None, key=DEFAULT_KEY):
            self.emitter = emitter
            self.key = key
            if rdb is None:
                rdb = redis.StrictRedis()
            self.rdb = rdb
            self.pool = Pool(5)

            signal.signal(signal.SIGTERM, self.request_shutdown)
            signal.signal(signal.SIGINT, self.request_shutdown)
            signal.signal(signal.SIGQUIT, self.request_shutdown)

        def send(self, payload):
            """
                Send an event to an emitter
            """
            self.emitter.input(payload)

        def pop_payload(self):
            """
                Get a single event from Redis and send it
                If the Redis queue is empty, sleep to avoid making continual requests
            """
            payload = self.rdb.lpop(self.key)
            if payload:
                self.pool.spawn(self.send, json.loads(payload.decode("utf-8")))
            else:
                gevent.sleep(5)

        def run(self):
            """
                Run indefinitely
            """
            self._shutdown = False

            while not self._shutdown:
                self.pop_payload()
            self.pool.join(timeout=20)

        def request_shutdown(self, *args):
            """
                Halt the worker
            """
            self._shutdown = True

    else:

        def __new__(cls, *args, **kwargs):
            raise RuntimeError('RedisWorker is not available. To use: `pip install snowplow-tracker[redis]`')
