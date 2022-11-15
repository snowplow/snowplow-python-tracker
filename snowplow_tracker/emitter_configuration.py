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
        
        self.buffer_size = buffer_size
        self.on_success = on_success
        self.on_failure = on_failure
        self.byte_limit = byte_limit
        self.request_timeout = request_timeout

        @property
        def buffer_size(self):
            return self.buffer_size
        
        @buffer_size.setter
        def buffer_size(self, value):
            self.buffer_size = value

        @property
        def on_success(self):
            return self.on_success
        
        @on_success.setter
        def on_success(self, value):
            self.on_success = value

        @property
        def on_failure(self):
            return self.on_failure
        
        @on_failure.setter
        def on_failure(self, value):
            self.on_failure = value
            
        @property
        def byte_limit(self):
            return self.byte_limit
        
        @byte_limit.setter
        def byte_limit(self, value):
            self.byte_limit = value

        @property
        def request_timeout(self):
            return self.request_timeout
        
        @request_timeout.setter
        def request_timeout(self, value):
            self.request_timeout = value
