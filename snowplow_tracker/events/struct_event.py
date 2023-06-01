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
from typing import Optional


class StructEvent(Event):
    def __init__(
        self,
        category: str,
        action: str,
        label: Optional[str] = None,
        property_: Optional[str] = None,
        value: Optional[int] = None,
    ) -> None:
        """
        :param  category:       Category of the event
        :type   category:       non_empty_string
        :param  action:         The event itself
        :type   action:         non_empty_string
        :param  label:          Refer to the object the action is
                                performed on
        :type   label:          string_or_none
        :param  property_:      Property associated with either the action
                                or the object
        :type   property_:      string_or_none
        :param  value:          A value associated with the user action
        :type   value:          int | float | None
        """
        super(StructEvent, self).__init__()
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
