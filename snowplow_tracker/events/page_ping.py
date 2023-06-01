# """
#     page_ping.py

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


class PagePing(Event):
    def __init__(
        self,
        page_url: Optional[str] = None,
        page_title: Optional[str] = None,
        referrer: Optional[str] = None,
        min_x: Optional[int] = None,
        max_x: Optional[int] = None,
        min_y: Optional[int] = None,
        max_y: Optional[int] = None,
    ) -> None:
        """
        :param  page_url:       URL of the viewed page
        :type   page_url:       non_empty_string
        :param  page_title:     Title of the viewed page
        :type   page_title:     string_or_none
        :param  referrer:       Referrer of the page
        :type   referrer:       string_or_none
        :param  min_x:          Minimum page x offset seen in the last ping period
        :type   min_x:          int | None
        :param  max_x:          Maximum page x offset seen in the last ping period
        :type   max_x:          int | None
        :param  min_y:          Minimum page y offset seen in the last ping period
        :type   min_y:          int | None
        :param  max_y:          Maximum page y offset seen in the last ping period
        :type   max_y:          int | None
        """
        super(PagePing, self).__init__()
        self.payload.add("e", "pp")
        self.page_url = page_url
        self.page_title = page_title
        self.referrer = referrer
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    @property
    def page_url(self) -> Optional[str]:
        """
        URL of the viewed page
        """
        return self._page_url

    @page_url.setter
    def page_url(self, value: Optional[str]):
        self._page_url = value
        self.payload.add("url", self._page_url)

    @property
    def page_title(self) -> Optional[str]:
        """
        URL of the viewed page
        """
        return self._page_title

    @page_title.setter
    def page_title(self, value: Optional[str]):
        self._page_title = value
        self.payload.add("page", self._page_title)

    @property
    def referrer(self) -> Optional[str]:
        """
        The referrer of the page
        """
        return self._referrer

    @referrer.setter
    def referrer(self, value: Optional[str]):
        self._referrer = value
        self.payload.add("refr", self._referrer)

    @property
    def min_x(self) -> Optional[int]:
        """
        Minimum page x offset seen in the last ping period
        """
        return self._min_x

    @min_x.setter
    def min_x(self, value: Optional[int]):
        self._min_x = value
        self.payload.add("pp_mix", self._min_x)

    @property
    def max_x(self) -> Optional[int]:
        """
        Maximum page x offset seen in the last ping period
        """
        return self._max_x

    @min_x.setter
    def max_x(self, value: Optional[int]):
        self._max_x = value
        self.payload.add("pp_max", self._max_x)

    @property
    def min_y(self) -> Optional[int]:
        """
        Minimum page y offset seen in the last ping period
        """
        return self._min_y

    @min_y.setter
    def min_y(self, value: Optional[int]):
        self._min_y = value
        self.payload.add("pp_miy", self._min_y)

    @property
    def max_y(self) -> Optional[int]:
        """
        Maximum page y offset seen in the last ping period
        """
        return self._max_y

    @min_y.setter
    def max_y(self, value: Optional[int]):
        self._max_y = value
        self.payload.add("pp_may", self._max_y)
