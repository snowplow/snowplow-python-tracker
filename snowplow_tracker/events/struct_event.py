# """
#     struct_event.py

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
from snowplow_tracker.events.event import Event
from typing import Optional, List
from snowplow_tracker import subject as _subject
from snowplow_tracker.self_describing_json import SelfDescribingJson


class StructEvent(Event):
    """
    Constructs a Structured event object.

    This event type is provided to be roughly equivalent to Google Analytics-style events.
    Note that it is not automatically clear what data should be placed in what field.
    To aid data quality and modeling, agree on business-wide definitions when designing
    your tracking strategy.

    We recommend using SelfDescribing - fully custom - events instead.

    When tracked, generates a "struct" or "se" event.
    """

    def __init__(
        self,
        category: str,
        action: str,
        event_subject: Optional[_subject.Subject] = None,
        context: Optional[List[SelfDescribingJson]] = None,
        tstamp: Optional[float] = None,
        label: Optional[str] = None,
        property_: Optional[str] = None,
        value: Optional[int] = None,
    ) -> None:
        """
        :param  category:       Category of the event
        :type   category:       non_empty_string
        :param  action:         The event itself
        :type   action:         non_empty_string
        :param  event_subject:   Optional per event subject
        :type   event_subject:   subject | None
        :param  context:         Custom context for the event
        :type   context:         context_array | None
        :param  tstamp:          Optional event timestamp in milliseconds
        :type   tstamp:          int | float | None
        :param  label:          Refer to the object the action is
                                performed on
        :type   label:          string_or_none
        :param  property_:      Property associated with either the action
                                or the object
        :type   property_:      string_or_none
        :param  value:          A value associated with the user action
        :type   value:          int | float | None
        """
        super(StructEvent, self).__init__(
            event_subject=event_subject, context=context, tstamp=tstamp
        )
        self.payload.add("e", "se")
        self.category = category
        self.action = action
        self.label = label
        self.property_ = property_
        self.value = value

    @property
    def category(self) -> Optional[str]:
        """
        Category of the event
        """
        return self._category

    @category.setter
    def category(self, value: Optional[str]):
        self._category = value
        self.payload.add("se_ca", self._category)

    @property
    def action(self) -> Optional[str]:
        """
        The event itself
        """
        return self._action

    @action.setter
    def action(self, value: Optional[str]):
        self._action = value
        self.payload.add("se_ac", self._action)

    @property
    def label(self) -> Optional[str]:
        """
        Refer to the object the action is performed on
        """
        return self._label

    @label.setter
    def label(self, value: Optional[str]):
        self._label = value
        self.payload.add("se_la", self._label)

    @property
    def property_(self) -> Optional[str]:
        """
        Property associated with either the action or the object
        """
        return self._property_

    @property_.setter
    def property_(self, value: Optional[str]):
        self._property_ = value
        self.payload.add("se_pr", self._property_)

    @property
    def value(self) -> Optional[int]:
        """
        A value associated with the user action
        """
        return self._value

    @value.setter
    def value(self, value: Optional[int]):
        self._value = value
        self.payload.add("se_va", self._value)
