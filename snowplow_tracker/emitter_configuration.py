# """
#     emitter_configuration.py

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

#     Authors: Jack Keene, Anuj More, Alex Dean, Fred Blundun, Paul Boocock
#     Copyright: Copyright (c) 2013-2022 Snowplow Analytics Ltd
#     License: Apache License Version 2.0
# """

from typing import Optional, Union, Tuple
from snowplow_tracker.typing import SuccessCallback, FailureCallback

class EmitterConfiguration(object):
    def __init__(
            self,
            buffer_size: Optional[int] = None,
            on_success: Optional[SuccessCallback] = None,
            on_failure: Optional[FailureCallback] = None,
            byte_limit: Optional[int] = None,
            request_timeout: Optional[Union[float, Tuple[float, float]]] = None) -> None:
        """
            Configuration for the emitter that sends events to the Snowplow collector.
            :param buffer_size:     The maximum number of queued events before the buffer is flushed. Default is 10.
            :type  buffer_size:     int | None
            :param on_success:      Callback executed after every HTTP request in a flush has status code 200
                                    Gets passed the number of events flushed.
            :type  on_success:      function | None
            :param on_failure:      Callback executed if at least one HTTP request in a flush has status code other than 200
                                    Gets passed two arguments:
                                    1) The number of events which were successfully sent
                                    2) If method is "post": The unsent data in string form;
                                       If method is "get":  An array of dictionaries corresponding to the unsent events' payloads
            :type  on_failure:      function | None
            :param byte_limit:      The size event list after reaching which queued events will be flushed
            :type  byte_limit:      int | None
            :param request_timeout: Timeout for the HTTP requests. Can be set either as single float value which
                                     applies to both "connect" AND "read" timeout, or as tuple with two float values
                                     which specify the "connect" and "read" timeouts separately
            :type request_timeout:  float | tuple | None
        """
        
        self.buffer_size = buffer_size
        self.on_success = on_success
        self.on_failure = on_failure
        self.byte_limit = byte_limit
        self.request_timeout = request_timeout

    @property
    def buffer_size(self):
        """
        The maximum number of queued events before the buffer is flushed. Default is 10.
        """
        return self._buffer_size

    @buffer_size.setter
    def buffer_size(self, value):
        if isinstance(value, int) and value < 0 or value is not None:
            raise ValueError("buffer_size must be of type int and greater than 0")    
        
        self._buffer_size = value

    @property
    def on_success(self):
        """
        Callback executed after every HTTP request in a flush has status code 200. Gets passed the number of events flushed.
        """
        return self._on_success

    @on_success.setter
    def on_success(self, value):
        self._on_success = value

    @property
    def on_failure(self):
        """
        Callback executed if at least one HTTP request in a flush has status code other than 200
                                Gets passed two arguments:
                                1) The number of events which were successfully sent
                                2) If method is "post": The unsent data in string form;
                                   If method is "get":  An array of dictionaries corresponding to the unsent events' payloads
        """
        return self._on_failure

    @on_failure.setter
    def on_failure(self, value):
        self._on_failure = value

    @property
    def byte_limit(self):
        """
        The size event list after reaching which queued events will be flushed
        """
        return self._byte_limit

    @byte_limit.setter
    def byte_limit(self, value):
        if isinstance(value, int) and value < 0 or value is not None:
            raise ValueError("byte_limit must be of type int and greater than 0")

        self._byte_limit = value   

    @property
    def request_timeout(self):
        """
        Timeout for the HTTP requests. Can be set either as single float value which
                                     applies to both "connect" AND "read" timeout, or as tuple with two float values
                                     which specify the "connect" and "read" timeouts separately
        """
        return self._request_timeout

    @request_timeout.setter
    def request_timeout(self, value):
        if isinstance(value, int) and value < 0 or value is not None:
            raise ValueError("request_timeout must be of type int and greater than 0")

        self._request_timeout = value    