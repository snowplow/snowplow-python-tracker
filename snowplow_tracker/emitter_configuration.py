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
        
        self.buffer_size = buffer_size
        self.on_success = on_success
        self.on_failure = on_failure
        self.byte_limit = byte_limit
        self.request_timeout = request_timeout