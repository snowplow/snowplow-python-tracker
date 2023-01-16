# """
#     event_store.py

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

from typing import Protocol
from snowplow_tracker.typing import PayloadDict, PayloadDictList


class EventStore(Protocol):
    event_buffer: object
    buffer_capacity: int
    
    def add_event(payload: PayloadDict) -> None:
        ... 
    def get_events_batch() -> PayloadDictList:
        ...
    def cleanup(need_retry: bool, batch: PayloadDictList) -> None:
        ...
    def size() -> int:
        ...
