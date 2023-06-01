# """
#     screen_view.py

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
from snowplow_tracker.constants import (
    UNSTRUCT_EVENT_SCHEMA,
    CONTEXT_SCHEMA,
    MOBILE_SCHEMA_PATH,
    SCHEMA_TAG,
)
from snowplow_tracker import payload
from snowplow_tracker import subject as _subject


class ScreenView(Event):
    """
    Constructs a ScreenView event object.

    When tracked, generates a SelfDescribing event (event type "ue").
    """

    def __init__(
        self,
        id_: Optional[str] = None,
        name: Optional[str] = None,
        type: Optional[str] = None,
        previous_name: Optional[str] = None,
        previous_id: Optional[str] = None,
        previous_type: Optional[str] = None,
        transition_type: Optional[str] = None,
    ) -> None:
        """
        :param  page_url:       URL of the viewed page
        :type   page_url:       non_empty_string
        :param  page_title:     Title of the viewed page
        :type   page_title:     string_or_none
        :param  referrer:       Referrer of the page
        :type   referrer:       string_or_none
        """
        super(ScreenView, self).__init__()
        self.payload.add("e", "ue")
        self.screen_view_properties = {}
        self.id_ = id_
        self.name = name
        self.type = type
        self.previous_name = previous_name
        self.previous_id = previous_id
        self.previous_type = previous_type
        self.transition_type = transition_type

    @property
    def id_(self) -> Optional[str]:
        """
        URL of the viewed page
        """
        return self._id_

    @id_.setter
    def id_(self, value: Optional[str]):
        self._id_ = value
        if self._id_ is not None:
            self.screen_view_properties["id"] = self._id_

    @property
    def name(self) -> Optional[str]:
        """
        URL of the viewed page
        """
        return self._name

    @name.setter
    def name(self, value: Optional[str]):
        self._name = value
        if self._name is not None:
            self.screen_view_properties["name"] = self._name

    @property
    def type(self) -> Optional[str]:
        """
        URL of the viewed page
        """
        return self._type

    @type.setter
    def type(self, value: Optional[str]):
        self._type = value
        if self._type is not None:
            self.screen_view_properties["type"] = self._type

    @property
    def previous_name(self) -> Optional[str]:
        """
        URL of the viewed page
        """
        return self._previous_name

    @previous_name.setter
    def previous_name(self, value: Optional[str]):
        self._previous_name = value
        if self._previous_name is not None:
            self.screen_view_properties["previousName"] = self._previous_name

    @property
    def previous_id(self) -> Optional[str]:
        """
        URL of the viewed page
        """
        return self._previous_id

    @previous_id.setter
    def previous_id(self, value: Optional[str]):
        self._previous_id = value
        if self._previous_id is not None:
            self.screen_view_properties["previousId"] = self._previous_id

    @property
    def previous_type(self) -> Optional[str]:
        """
        URL of the viewed page
        """
        return self._previous_type

    @previous_type.setter
    def previous_type(self, value: Optional[str]):
        self._previous_type = value
        if self._previous_type is not None:
            self.screen_view_properties["previousType"] = self._previous_type

    @property
    def transition_type(self) -> Optional[str]:
        """
        URL of the viewed page
        """
        return self._transition_type

    @transition_type.setter
    def transition_type(self, value: Optional[str]):
        self._transition_type = value
        if self._transition_type is not None:
            self.screen_view_properties["transitionType"] = self._transition_type

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
            self.payload.add_json(
                context_envelope, encode_base64, "cx", "co", json_encoder
            )

        if isinstance(
            tstamp,
            (
                int,
                float,
            ),
        ):
            self.payload.add("ttm", int(tstamp))

        self.payload.add_dict(event_subject.standard_nv_pairs)

        event_json = SelfDescribingJson(
            "%s/screen_view/%s/1-0-0" % (MOBILE_SCHEMA_PATH, SCHEMA_TAG),
            self.screen_view_properties,
        )

        envelope = SelfDescribingJson(
            UNSTRUCT_EVENT_SCHEMA, event_json.to_json()
        ).to_json()
        self.payload.add_json(envelope, encode_base64, "ue_px", "ue_pr", json_encoder)

        return self.payload
