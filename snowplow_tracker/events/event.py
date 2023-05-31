# """
#     event.py

#     Copyright (c) 2013-2023 Snowplow Analytics Ltd. All rights reserved.

#     This program is licensed to you under the Apache License Version 2.0,
#     and you may not use this file except in compliance with the Apache License
#     Version 2.0. You may obtain a copy of the Apache License Version 2.0 at
#     http://www.apache.org/licenses/LICENSE-2.0.

#     Unless required by applicable law or agreed to in writing,
#     software distributed under the Apache License Version 2.0 is distributed on
#     an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#     express or implied. See the Apache License Version 2.0 for the specific
#     language governing permissions and limitations there under.
# """

from typing import Optional, List
from snowplow_tracker import payload
from snowplow_tracker import subject as _subject

from snowplow_tracker.self_describing_json import SelfDescribingJson

from snowplow_tracker.constants import CONTEXT_SCHEMA
from snowplow_tracker.typing import JsonEncoderFunction, PayloadDict


class Event(object):
    def __init__(self, dict_: Optional[PayloadDict] = None) -> None:
        """
        Constructor
        """
        self.pb = payload.Payload(dict_=dict_)

    def build_payload(
        self,
        event_subject: Optional[_subject.Subject],
        encode_base64: bool,
        json_encoder: Optional[JsonEncoderFunction],
        tstamp: Optional[float],
        context: Optional[List[SelfDescribingJson]],
    ) -> "payload.Payload":
        """
        :param  event_subject:   Optional per event subject
        :type   event_subject:   subject | None
        :param encode_base64:    Whether JSONs in the payload should be base-64 encoded
        :type  encode_base64:    bool
        :param json_encoder:     Custom JSON serializer that gets called on non-serializable object
        :type  json_encoder:     function | None
        :param  tstamp:          Optional event timestamp in milliseconds
        :type   tstamp:          int | float | None
        :param  context:         Custom context for the event
        :type   context:         context_array | None
        :rtype:                  payload.Payload
        """
        if context is not None:
            context_jsons = list(map(lambda c: c.to_json(), context))
            context_envelope = SelfDescribingJson(
                CONTEXT_SCHEMA, context_jsons
            ).to_json()
            self.pb.add_json(context_envelope, encode_base64, "cx", "co", json_encoder)

        if isinstance(
            tstamp,
            (
                int,
                float,
            ),
        ):
            self.pb.add("ttm", int(tstamp))

        self.pb.add_dict(event_subject.standard_nv_pairs)
        return self.pb
