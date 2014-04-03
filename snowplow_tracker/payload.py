"""
    payload.py

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

    Authors: Anuj More, Alex Dean
    Copyright: Copyright (c) 2013-2014 Snowplow Analytics Ltd
    License: Apache License Version 2.0
"""


import random
import time
import json
import base64
from contracts import contract


class Payload:

    def __init__(self, tstamp=None, dict_=None):
        """
            Constructor
        """

        self.context = {}
        # Set transaction for every event
        self.context['tid'] = Payload.set_transaction_id()
        # Set timestamp for every event
        self.set_timestamp(tstamp)
        if dict_ is not None:
            for f in dict_:
                self.context[f] = dict_[f]

    """
    Special payload creation functions
    """
    @staticmethod
    def set_transaction_id():
        """
            Set transaction ID for the payload once during the lifetime of the
            event.
        """
        tid = random.randrange(100000, 999999)
        return tid

    def set_timestamp(self, tstamp=None):
        """
            Set timestamp and allow rewriting it multiple times.

            :param  tstamp:         Timestamp value
        """
        if tstamp is None:
            tstamp = time.time()
        if tstamp and isinstance(tstamp, (int, float)):
            value = int(tstamp * 1000)
        else:
            value = tstamp
        self.context['dtm'] = value

    """
    Payload creators
    """

    def add(self, name, value):
        """
            Add a name value pair to the Payload object
        """
        if not (value == '' or value is None):
            self.context[name] = value

    @contract
    def add_dict(self, dict_, base64=False):
        """
            Add a dict of name value pairs to the Payload object

            :param  dict_:          Dictionary to be added to the Payload
            :type   dict_:          dict(*:*)
        """
        for f in dict_:
            self.add(f, dict_[f])

    @contract
    def add_unstruct(self, dict_, encode_base64,
                     type_when_encoded, type_when_not_encoded):
        """
            Add an encoded or unencoded JSON to the payload after verifying
            the contents of the dict

            :param  dict_:      Dictionary of the payload to be generated
            :type   dict_:      dict(str:*)
            :param  encode_base64:      If the payload is base64 encoded
            :type   encode_base64:      bool
            :param  type_when_encoded:  Name of the field when encode_base64
                                        is set
            :type   type_when_encoded:  str
            :param  type_when_not_encoded:  Name of the field when
                                            encode_base64 is not set
            :type   type_when_not_encoded:  str
        """
        def raise_error(f, type_):
            raise RuntimeError(''.join([f, " in dict is not a ", type_]))

        types = ["int", "flt", "geo", "dt", "ts", "tms"]

        for f in dict_:
            parts = f.split("$")
            if parts[-1] in types:
                type_ = parts[-1]
                if ((type_ == "int" and not isinstance(dict_[f], int)) or
                    (type_ == "flt" and not isinstance(dict_[f], float)) or
                    (type_ == "geo" and not isinstance(dict_[f], tuple)) or
                    (type_ == "dt" and not isinstance(dict_[f], int)) or
                    (type_ == "ts" and not isinstance(dict_[f], int)) or
                    (type_ == "tms" and not isinstance(dict_[f], int))):
                    raise_error(f, type_)
        json_dict = json.dumps(dict_)

        if encode_base64:
            self.add(type_when_encoded, base64.urlsafe_b64encode(json_dict.encode('ascii')))
        else:
            self.add(type_when_not_encoded, json_dict)

    def get(self):
        """
            Returns the context dictionary from the Payload object
        """
        return self.context
