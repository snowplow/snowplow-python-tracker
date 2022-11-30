# """
#     emitters.py

#     Copyright (c) 2013-2022 Snowplow Analytics Ltd. All rights reserved.

#     This program is licensed to you under the Apache License Version 2.0,
#     and you may not use this file except in compliance with the Apache License
#     Version 2.0. You may obtain a copy of the Apache License Version 2.0 at
#     http://www.apache.org/licenses/LICENSE-2.0.

#     Unless required by applicable law or agreed to in writing,
#     software distributed under the Apache License Version 2.0 is distributed on
#     an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#     express or implied. See the Apache License Version 2.0 for the specific
#     language governing permissions and limitations there under.

#     Authors: Anuj More, Alex Dean, Fred Blundun, Paul Boocock
#     Copyright: Copyright (c) 2013-2022 Snowplow Analytics Ltd
#     License: Apache License Version 2.0
# """


import logging
import time
import threading
import requests
import random
from typing import Optional, Union, Tuple
from queue import Queue

from snowplow_tracker.self_describing_json import SelfDescribingJson
from snowplow_tracker.typing import (
    PayloadDict,
    PayloadDictList,
    HttpProtocol,
    Method,
    SuccessCallback,
    FailureCallback,
)
from snowplow_tracker.contracts import one_of

# logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DEFAULT_MAX_LENGTH = 10
PAYLOAD_DATA_SCHEMA = (
    "iglu:com.snowplowanalytics.snowplow/payload_data/jsonschema/1-0-4"
)
PROTOCOLS = {"http", "https"}
METHODS = {"get", "post"}


class Emitter(object):
    """
    Synchronously send Snowplow events to a Snowplow collector
    Supports both GET and POST requests
    """

    def __init__(
        self,
        endpoint: str,
        protocol: HttpProtocol = "https",
        port: Optional[int] = None,
        method: Method = "post",
        buffer_size: Optional[int] = None,
        on_success: Optional[SuccessCallback] = None,
        on_failure: Optional[FailureCallback] = None,
        byte_limit: Optional[int] = None,
        request_timeout: Optional[Union[float, Tuple[float, float]]] = None,
        retry_codes={},
        max_retry=60,
    ) -> None:
        """
        :param endpoint:    The collector URL. If protocol is not set in endpoint it will automatically set to "https://" - this is done automatically.
        :type  endpoint:    string
        :param protocol:    The protocol to use - http or https. Defaults to https.
        :type  protocol:    protocol
        :param port:        The collector port to connect to
        :type  port:        int | None
        :param method:      The HTTP request method. Defaults to post.
        :type  method:      method
        :param buffer_size: The maximum number of queued events before the buffer is flushed. Default is 10.
        :type  buffer_size: int | None
        :param on_success:  Callback executed after every HTTP request in a flush has status code 200
                            Gets passed the number of events flushed.
        :type  on_success:  function | None
        :param on_failure:  Callback executed if at least one HTTP request in a flush has status code other than 200
                            Gets passed two arguments:
                            1) The number of events which were successfully sent
                            2) If method is "post": The unsent data in string form;
                               If method is "get":  An array of dictionaries corresponding to the unsent events' payloads
        :type  on_failure:  function | None
        :param byte_limit:  The size event list after reaching which queued events will be flushed
        :type  byte_limit:  int | None
        :param request_timeout: Timeout for the HTTP requests. Can be set either as single float value which
                                 applies to both "connect" AND "read" timeout, or as tuple with two float values
                                 which specify the "connect" and "read" timeouts separately
        :type request_timeout:  float | tuple | None
        """
        one_of(protocol, PROTOCOLS)
        one_of(method, METHODS)

        self.endpoint = Emitter.as_collector_uri(endpoint, protocol, port, method)

        self.method = method

        if buffer_size is None:
            if method == "post":
                buffer_size = DEFAULT_MAX_LENGTH
            else:
                buffer_size = 1
        self.buffer_size = buffer_size
        self.buffer = []
        self.byte_limit = byte_limit
        self.bytes_queued = None if byte_limit is None else 0
        self.request_timeout = request_timeout

        self.on_success = on_success
        self.on_failure = on_failure

        self.lock = threading.RLock()

        self.timer = None

        self.retry_codes = retry_codes
        self.max_retry = max_retry
        self.retry_delay = 0

        logger.info("Emitter initialized with endpoint " + self.endpoint)

    @staticmethod
    def as_collector_uri(
        endpoint: str,
        protocol: HttpProtocol = "https",
        port: Optional[int] = None,
        method: Method = "post",
    ) -> str:
        """
        :param endpoint:  The raw endpoint provided by the user
        :type  endpoint:  string
        :param protocol:  The protocol to use - http or https
        :type  protocol:  protocol
        :param port:      The collector port to connect to
        :type  port:      int | None
        :param method:    Either `get` or `post` HTTP method
        :type  method:    method
        :rtype:           string
        """
        if len(endpoint) < 1:
            raise ValueError("No endpoint provided.")

        endpoint = endpoint.rstrip('/')

        if endpoint.split("://")[0] in PROTOCOLS:
            endpoint_arr = endpoint.split("://")
            protocol = endpoint_arr[0]
            endpoint = endpoint_arr[1]

        if method == "get":
            path = "/i"
        else:
            path = "/com.snowplowanalytics.snowplow/tp2"
        if port is None:
            return protocol + "://" + endpoint + path
        else:
            return protocol + "://" + endpoint + ":" + str(port) + path

    def input(self, payload: PayloadDict) -> None:
        """
        Adds an event to the buffer.
        If the maximum size has been reached, flushes the buffer.

        :param payload:   The name-value pairs for the event
        :type  payload:   dict(string:\\*)
        """
        with self.lock:
            if self.bytes_queued is not None:
                self.bytes_queued += len(str(payload))

            if self.method == "post":
                self.buffer.append({key: str(payload[key]) for key in payload})
            else:
                self.buffer.append(payload)

            if self.reached_limit():
                self.flush()

    def reached_limit(self) -> bool:
        """
        Checks if event-size or bytes limit are reached

        :rtype: bool
        """
        if self.byte_limit is None:
            return len(self.buffer) >= self.buffer_size
        else:
            return (self.bytes_queued or 0) >= self.byte_limit or len(
                self.buffer
            ) >= self.buffer_size

    def flush(self) -> None:
        """
        Sends all events in the buffer to the collector.
        """
        with self.lock:
            self.send_events(self.buffer)
            self.buffer = []
            if self.bytes_queued is not None:
                self.bytes_queued = 0

    def http_post(self, data: str) -> int:
        """
        :param data:  The array of JSONs to be sent
        :type  data:  string
        """
        logger.info("Sending POST request to %s..." % self.endpoint)
        logger.debug("Payload: %s" % data)
        try:
            r = requests.post(
                self.endpoint,
                data=data,
                headers={"Content-Type": "application/json; charset=utf-8"},
                timeout=self.request_timeout,
            )
        except requests.RequestException as e:
            logger.warning(e)

        return r.status_code

    def http_get(self, payload: PayloadDict) -> int:
        """
        :param payload:  The event properties
        :type  payload:  dict(string:\\*)
        """
        logger.info("Sending GET request to %s..." % self.endpoint)
        logger.debug("Payload: %s" % payload)
        try:
            r = requests.get(
                self.endpoint, params=payload, timeout=self.request_timeout
            )
        except requests.RequestException as e:
            logger.warning(e)

        return r.status_code

    def sync_flush(self) -> None:
        """
        Calls the flush method of the base Emitter class.
        This is guaranteed to be blocking, not asynchronous.
        """
        logger.debug("Starting synchronous flush...")
        Emitter.flush(self)
        logger.info("Finished synchronous flush")

    @staticmethod
    def is_good_status_code(status_code: int) -> bool:
        """
        :param status_code:  HTTP status code
        :type  status_code:  int
        :rtype:              bool
        """
        return 200 <= status_code < 300

    def send_events(self, evts: PayloadDictList) -> None:
        """
        :param evts: Array of events to be sent
        :type  evts: list(dict(string:\\*))
        """
        if len(evts) > 0:
            logger.info("Attempting to send %s events" % len(evts))

            Emitter.attach_sent_timestamp(evts)
            success_events = []
            failure_events = []

            if self.method == "post":
                data = SelfDescribingJson(PAYLOAD_DATA_SCHEMA, evts).to_string()
                status_code = self.http_post(data)
                request_succeeded = Emitter.is_good_status_code(status_code)
                if request_succeeded:
                    success_events += evts
                else:
                    failure_events += evts

            elif self.method == "get":
                for evt in evts:
                    status_code = self.http_get(evt)
                    request_succeeded = Emitter.is_good_status_code(status_code)

                    if request_succeeded:
                        success_events += [evt]
                    else:
                        failure_events += [evt]

            if self.on_success is not None and len(success_events) > 0:
                self.on_success(success_events)
            if self.on_failure is not None and len(failure_events) > 0:
                self.on_failure(len(success_events), failure_events)

        else:
            logger.info("Skipping flush since buffer is empty")

    def set_flush_timer(self, timeout: float, flush_now: bool = False) -> None:
        """
        Set an interval at which the buffer will be flushed

        :param timeout:   interval in seconds
        :type  timeout:   int | float
        :param flush_now: immediately flush buffer
        :type  flush_now: bool
        """

        # Repeatable create new timer
        if flush_now:
            self.flush()
        self.timer = threading.Timer(timeout, self.set_flush_timer, [timeout, True])
        self.timer.daemon = True
        self.timer.start()

    def cancel_flush_timer(self) -> None:
        """
        Abort automatic async flushing
        """

        if self.timer is not None:
            self.timer.cancel()

    @staticmethod
    def attach_sent_timestamp(events: PayloadDictList) -> None:
        """
        Attach (by mutating in-place) current timestamp in milliseconds
        as `stm` param

        :param events: Array of events to be sent
        :type  events: list(dict(string:\\*))
        :rtype: None
        """

        def update(e: PayloadDict) -> None:
            e.update({"stm": str(int(time.time()) * 1000)})

        for event in events:
            update(event)

    def should_retry(self, status_code: int) -> bool:
        if Emitter.is_good_status_code(status_code):
            return False

        if status_code in self.retry_codes.keys():
            return self.retry_codes[status_code]

        return not status_code in [400, 401, 403, 410, 422]

    def set_retry_delay(self) -> None:
        random_noise = random.random()
        self.retry_delay = min(self.retry_delay * 2 + random_noise, self.max_retry)

    def reset_retry_delay(self) -> None:
        self.retry_delay = 0

    def failure_retry(self, failed_events):
        for event in failed_events:
            if not event in self.buffer:
                self.buffer.append(event)

        self.set_flush_timer(self.retry_delay)


class AsyncEmitter(Emitter):
    """
    Uses threads to send HTTP requests asynchronously
    """

    def __init__(
        self,
        endpoint: str,
        protocol: HttpProtocol = "http",
        port: Optional[int] = None,
        method: Method = "post",
        buffer_size: Optional[int] = None,
        on_success: Optional[SuccessCallback] = None,
        on_failure: Optional[FailureCallback] = None,
        thread_count: int = 1,
        byte_limit: Optional[int] = None,
    ) -> None:
        """
        :param endpoint:    The collector URL. Don't include "http://" - this is done automatically.
        :type  endpoint:    string
        :param protocol:    The protocol to use - http or https. Defaults to http.
        :type  protocol:    protocol
        :param port:        The collector port to connect to
        :type  port:        int | None
        :param method:      The HTTP request method
        :type  method:      method
        :param buffer_size: The maximum number of queued events before the buffer is flushed. Default is 10.
        :type  buffer_size: int | None
        :param on_success:  Callback executed after every HTTP request in a flush has status code 200
                            Gets passed the number of events flushed.
        :type  on_success:  function | None
        :param on_failure:  Callback executed if at least one HTTP request in a flush has status code other than 200
                            Gets passed two arguments:
                            1) The number of events which were successfully sent
                            2) If method is "post": The unsent data in string form;
                               If method is "get":  An array of dictionaries corresponding to the unsent events' payloads
        :type  on_failure:  function | None
        :param thread_count: Number of worker threads to use for HTTP requests
        :type  thread_count: int
        :param byte_limit:  The size event list after reaching which queued events will be flushed
        :type  byte_limit:  int | None
        """
        super(AsyncEmitter, self).__init__(
            endpoint,
            protocol,
            port,
            method,
            buffer_size,
            on_success,
            on_failure,
            byte_limit,
        )
        self.queue = Queue()
        for i in range(thread_count):
            t = threading.Thread(target=self.consume)
            t.daemon = True
            t.start()

    def sync_flush(self) -> None:
        while True:
            self.flush()
            self.queue.join()
            if len(self.buffer) < 1:
                break

    def flush(self) -> None:
        """
        Removes all dead threads, then creates a new thread which
        executes the flush method of the base Emitter class
        """
        with self.lock:
            self.queue.put(self.buffer)
            self.buffer = []
            if self.bytes_queued is not None:
                self.bytes_queued = 0

    def consume(self) -> None:
        while True:
            evts = self.queue.get()
            self.send_events(evts)
            self.queue.task_done()
