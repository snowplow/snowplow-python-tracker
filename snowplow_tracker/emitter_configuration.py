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