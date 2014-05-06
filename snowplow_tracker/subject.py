"""
    subject.py

    Copyright (c) 2013-2014 Snowplow Analytics Ltd. All rights reserved.

    This program is licensed to you under the Apache License Version 2.0,
    and you may not use this file except in compliance with the Apache License
    Version 2.0. You may obtain a copy of the Apache License Version 2.0 at
    http://www.apache.org/licenses/LICENSE-2.0.

    Unless required by applicable law or agreed to in writing,
    software distributed under the Apache License Version 2.0 is distributed on
    an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
    express or implied. See the Apache License Version 2.0 for the specific
    language governing permissions and limitations there under.

    Authors: Anuj More, Alex Dean, Fred Blundun
    Copyright: Copyright (c) 2013-2014 Snowplow Analytics Ltd
    License: Apache License Version 2.0
"""

from contracts import contract, new_contract

new_contract("subject", lambda x: isinstance(x, Subject))

SUPPORTED_PLATFORMS = set(["pc", "tv", "mob", "cnsl", "iot"])
DEFAULT_PLATFORM = "pc"

class Subject(object):
    """
        Class for an event subject, where we view events as of the form

        (Subject) -> (Verb) -> (Object)
    """
    def __init__(self):

        self.standard_nv_pairs = {"p": DEFAULT_PLATFORM}

    @contract
    def set_platform(self, value):
        """
            :param  value:          One of ["pc", "tv", "mob", "cnsl", "iot"]
            :type   value:          str
            :rtype:                 subject
        """
        if value in SUPPORTED_PLATFORMS:
            self.standard_nv_pairs["p"] = value
        else:
            raise RuntimeError(value + " is not a supported platform")
        return self

    @contract
    def set_user_id(self, user_id):
        """
            :param  user_id:        User ID
            :type   user_id:        non_empty_string
            :rtype:                 subject
        """
        self.standard_nv_pairs["uid"] = user_id
        return self

    @contract
    def set_screen_resolution(self, width, height):
        """
            :param  width:          Width of the screen
            :param  height:         Height of the screen
            :type   width:          int,>0
            :type   height:         int,>0
            :rtype:                 subject
        """
        self.standard_nv_pairs["res"] = "".join([str(width), "x", str(height)])
        return self

    @contract
    def set_viewport(self, width, height):
        """
            :param  width:          Width of the viewport
            :param  height:         Height of the viewport
            :type   width:          int,>0
            :type   height:         int,>0
            :rtype:                 subject
        """
        self.standard_nv_pairs["vp"] = "".join([str(width), "x", str(height)])
        return self

    @contract
    def set_color_depth(self, depth):
        """
            :param  depth:          Depth of the color on the screen
            :type   depth:          int
            :rtype:                 subject
        """
        self.standard_nv_pairs["cd"] = depth
        return self

    @contract
    def set_timezone(self, timezone):
        """
            :param  timezone:       Timezone as a string
            :type   timezone:       non_empty_string
            :rtype:                 subject
        """
        self.standard_nv_pairs["tz"] = timezone
        return self

    @contract
    def set_lang(self, lang):
        """
            Set language.

            :param  lang:           Language the application is set to
            :type   lang:           non_empty_string
            :rtype:                 subject
        """
        self.standard_nv_pairs["lang"] = lang
        return self
