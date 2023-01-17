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

from typing_extensions import Protocol
from snowplow_tracker.typing import PayloadDict, PayloadDictList


class EventStore(Protocol):
    def add_event(payload: PayloadDict) -> None:
        ...

    def get_events_batch() -> PayloadDictList:
        ...

    def cleanup(need_retry: bool, batch: PayloadDictList) -> None:
        ...

    def size() -> int:
        ...


class InMemoryEventStore(EventStore):
    def __init__(self, buffer_capacity: int = 10000) -> None:

        self.event_buffer = []
        self.buffer_capacity = buffer_capacity

    def add_event(self, payload: PayloadDict) -> None:
        self.event_buffer.append(payload)

    def get_events_batch(self) -> PayloadDictList:
        batch = self.event_buffer
        self.event_buffer = []
        return batch

    def cleanup(self, batch: PayloadDictList, need_retry: bool = False) -> None:
        if need_retry:
            self.event_buffer.append(batch)
            return
        self.event_buffer = []

    def size(self) -> int:
        return len(self.event_buffer)
