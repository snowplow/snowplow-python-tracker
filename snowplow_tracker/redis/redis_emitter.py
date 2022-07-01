"""
    redis_emitter.py

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
import logging
from typing import Any, Optional
from snowplow_tracker.typing import PayloadDict, RedisProtocol

_REDIS_OPT = True
try:
    import redis
except ImportError:
    _REDIS_OPT = False

# logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RedisEmitter(object):
    """
        Sends Snowplow events to a Redis database
    """
    if _REDIS_OPT:

        def __init__(self, rdb: Optional[RedisProtocol] = None, key: str = "snowplow") -> None:
            """
                :param rdb:  Optional custom Redis database
                :type  rdb:  redis | None
                :param key:  The Redis key for the list of events
                :type  key:  string
            """
            if rdb is None:
                rdb = redis.StrictRedis()

            self.rdb = rdb
            self.key = key

        def input(self, payload: PayloadDict) -> None:
            """
                :param payload:  The event properties
                :type  payload:  dict(string:*)
            """
            logger.debug("Pushing event to Redis queue...")
            self.rdb.rpush(self.key, json.dumps(payload))
            logger.info("Finished sending event to Redis.")

        def flush(self) -> None:
            logger.warning("The RedisEmitter class does not need to be flushed")

        def sync_flush(self) -> None:
            self.flush()

    else:

        def __new__(cls, *args: Any, **kwargs: Any) -> 'RedisEmitter':
            logger.error("RedisEmitter is not available. Please install snowplow-tracker with redis extra dependency.")
            raise RuntimeError('RedisEmitter is not available. To use: `pip install snowplow-tracker[redis]`')
