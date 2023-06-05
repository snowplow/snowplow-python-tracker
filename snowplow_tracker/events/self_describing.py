# """
#     self_describing.py

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
from snowplow_tracker.typing import JsonEncoderFunction
from snowplow_tracker.events.event import Event
from snowplow_tracker import SelfDescribingJson
from snowplow_tracker.constants import UNSTRUCT_EVENT_SCHEMA
from snowplow_tracker import payload
from snowplow_tracker import subject as _subject
from snowplow_tracker.constants import CONTEXT_SCHEMA


class SelfDescribing(Event):
    """
    Constructs a SelfDescribing event object.

    This is a customisable event type which allows you to track anything describable
    by a JsonSchema.

    When tracked, generates a self-describing event (event type "ue").
    """

    def __init__(
        self,
        event_json: SelfDescribingJson,
        event_subject: Optional[_subject.Subject] = None,
        context: Optional[List[SelfDescribingJson]] = None,
        tstamp: Optional[float] = None,
    ) -> None:
        """
        :param  event_json:      The properties of the event. Has two field:
                                 A "data" field containing the event properties and
                                 A "schema" field identifying the schema against which the data is validated
        :type   event_json:      self_describing_json
        :param encode_base64:    Whether JSONs in the payload should be base-64 encoded
        :type  encode_base64:    bool
        :param json_encoder:     Custom JSON serializer that gets called on non-serializable object
        :type  json_encoder:     function | None
        """
        super(SelfDescribing, self).__init__(
            event_subject=event_subject, context=context, tstamp=tstamp
        )
        self.payload.add("e", "ue")
        self.event_json = event_json

    @property
    def event_json(self) -> SelfDescribingJson:
        """
        The properties of the event. Has two field:
            A "data" field containing the event properties and
            A "schema" field identifying the schema against which the data is validated
        """
        return self._event_json

    @event_json.setter
    def event_json(self, value: SelfDescribingJson):
        self._event_json = value

    def build_payload(
        self,
        encode_base64: bool,
        json_encoder: Optional[JsonEncoderFunction],
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
        if self.context is not None:
            context_jsons = list(map(lambda c: c.to_json(), self.context))
            context_envelope = SelfDescribingJson(
                CONTEXT_SCHEMA, context_jsons
            ).to_json()
            self.payload.add_json(
                context_envelope, encode_base64, "cx", "co", json_encoder
            )

        if isinstance(
            self.tstamp,
            (
                int,
                float,
            ),
        ):
            self.payload.add("ttm", int(self.tstamp))

        if self.event_subject is not None:
            self.payload.add_dict(self.event_subject.standard_nv_pairs)

        envelope = SelfDescribingJson(
            UNSTRUCT_EVENT_SCHEMA, self.event_json.to_json()
        ).to_json()
        self.payload.add_json(envelope, encode_base64, "ue_px", "ue_pr", json_encoder)

        return self.payload
