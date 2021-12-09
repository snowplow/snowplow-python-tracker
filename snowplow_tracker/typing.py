"""
    typing.py

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

    Authors: Anuj More, Alex Dean, Fred Blundun, Paul Boocock, Matus Tomlein
    Copyright: Copyright (c) 2013-2021 Snowplow Analytics Ltd
    License: Apache License Version 2.0
"""

from typing import Dict, List, Callable, Any, Optional
from typing_extensions import Protocol, Literal

PayloadDict = Dict[str, Any]
PayloadDictList = List[PayloadDict]
JsonEncoderFunction = Callable[[Any], Any]

HttpProtocol = Literal["http", "https"]
Method = Literal["get", "post"]


class EmitterProtocol(Protocol):
    def input(self, payload: PayloadDict) -> None:
        ...


class RedisProtocol(Protocol):
    def rpush(self, name: Any, *values: Any) -> int:
        ...

    def lpop(self, name: Any, count: Optional[int] = ...) -> Any:
        ...
