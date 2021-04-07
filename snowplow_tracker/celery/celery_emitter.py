"""
    celery_emitter.py

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

import logging
from snowplow_tracker.emitters import Emitter

_CELERY_OPT = True
try:
    from celery import Celery
except ImportError:
    _CELERY_OPT = False

# logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class CeleryEmitter(Emitter):
    """
        Uses a Celery worker to send HTTP requests asynchronously.
        Works like the base Emitter class,
        but on_success and on_failure callbacks cannot be set.
    """
    if _CELERY_OPT:

        celery_app = None

        def __init__(self, endpoint, protocol="http", port=None, method="get", buffer_size=None, byte_limit=None):
            super(CeleryEmitter, self).__init__(endpoint, protocol, port, method, buffer_size, None, None, byte_limit)

            try:
                # Check whether a custom Celery configuration module named "snowplow_celery_config" exists
                import snowplow_celery_config
                self.celery_app = Celery()
                self.celery_app.config_from_object(snowplow_celery_config)
            except ImportError:
                # Otherwise configure Celery with default settings
                self.celery_app = Celery("Snowplow", broker="redis://guest@localhost//")

            self.async_flush = self.celery_app.task(self.async_flush)

        def flush(self):
            """
            Schedules a flush task
            """
            self.async_flush.delay()
            logger.info("Scheduled a Celery task to flush the event queue")

        def async_flush(self):
            super(CeleryEmitter, self).flush()

    else:

        def __new__(cls, *args, **kwargs):
            logger.error("CeleryEmitter is not available. Please install snowplow-tracker with celery extra dependency.")
            raise RuntimeError('CeleryEmitter is not available. To use: `pip install snowplow-tracker[celery]`')
