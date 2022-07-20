# """
#     self_describing_json.py

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

import json
from typing import Union

from snowplow_tracker.typing import PayloadDict, PayloadDictList


class SelfDescribingJson(object):

    def __init__(self, schema: str, data: Union[PayloadDict, PayloadDictList]) -> None:
        self.schema = schema
        self.data = data

    def to_json(self) -> PayloadDict:
        return {
            "schema": self.schema,
            "data": self.data
        }

    def to_string(self) -> str:
        return json.dumps(self.to_json())
