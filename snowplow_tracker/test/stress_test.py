#!/usr/bin/env python

# TODO: add atomic (because AsyncEmitter works on threads) counter for requests
# TODO: add timings

import uuid

from snowplow_tracker import Tracker, AsyncEmitter


COLLECTOR = ''
BUFFER_SIZE = 10


class StressTest(object):
    """Container for mutable state of Python Tracker stress test

    Usage:
    >>> continer = StressTest()
    >>> continer.start(100)     # Where 100 is load size, need to be increased
    """
    def __init__(self):
        emitter = AsyncEmitter(COLLECTOR,
                               protocol='http',
                               port=80,
                               method='post',
                               buffer_size=BUFFER_SIZE,
                               thread_count=4,
                               on_success=self.store_success,
                               on_failure=self.store_failure)
        self.successes = []
        self.failures = []
        self.tracker = Tracker(emitter,
                               app_id='python-stress-test',
                               encode_base64=False)

    def generate_event(self):
        rnd = uuid.uuid4().get_hex()
        page_view = {
            'pageUrl': 'http://example.com/' + rnd,
            'pageTitle': rnd,
            'referrer': rnd
        }
        self.tracker.track_page_view(page_view['pageUrl'],
                                     page_view['pageTitle'],
                                     page_view['referrer'])

    def start(self, load_size):
        for _ in range(load_size):
            self.generate_event()

    def store_success(self, result):
        self.successes.append(result)

    def store_failure(self, result):
        self.failures.append(result)
