"""
    tracker.py

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

import requests
from snowplow_tracker import payload, _version
from contracts import contract, new_contract, disable_all

"""
Constants & config
"""

VERSION = "py-%s" % _version.__version__
DEFAULT_ENCODE_BASE64 = True
DEFAULT_PLATFORM = "pc"
SUPPORTED_PLATFORMS = set(["pc", "tv", "mob", "cnsl", "iot"])
DEFAULT_VENDOR = "com.snowplowanalytics"


"""
Tracker class
"""


class Tracker:

    new_contract("non_empty_string", lambda s: isinstance(s, str)
                 and len(s) > 0)
    new_contract("string_or_none", lambda s: (isinstance(s, str)
                 and len(s) > 0) or s is None)
    new_contract("payload", lambda s: isinstance(s, payload.Payload))

    def __init__(self, collector_uri, namespace="", contracts=True):
        """
        Constructor
        """
        if not contracts:
            disable_all()

        self.collector_uri = self.as_collector_uri(collector_uri)

        self.config = {
            "encode_base64":    DEFAULT_ENCODE_BASE64
        }

        self.standard_nv_pairs = {
            "p": DEFAULT_PLATFORM,
            "tv": VERSION,
            "tna": namespace
        }

    @contract
    def as_collector_uri(self, host):
        """
            Method to create a URL

            :param  host:        URL input by user
            :type   host:        str
            :rtype:              str
        """
        return "".join(["http://", host, "/i"])

    """
    Fire a GET request
    """

    @contract
    def http_get(self, payload):
        """
            Send a GET request to the collector URI (generated from the
            new_tracker methods) and return the relevant error message if any.

            :param  payload:        Generated dict track()
            :type   payload:        payload
        """

        r = requests.get(self.collector_uri, params=payload.context)
        code = r.status_code
        if code < 0 or code > 600:
            return "".join(["Unrecognised status code [", str(code), "]"])
        elif code >= 400 and code < 500:
            return "".join(["HTTP status code [", str(code),
                            "] is a client error"])
        elif code >= 500:
            return "".join(["HTTP status code [", str(code),
                            "] is a server error"])
        return r.url

    """
    Setter methods
    """

    @contract
    def set_base64_to(self, value):
        """
            :param  value:          Boolean value
            :type   value:          bool
        """
        self.config["encode_base64"] = value

    @contract
    def set_platform(self, value):
        """
            :param  value:          One of ["pc", "tv", "mob", "cnsl", "iot"]
            :type   value:          str
        """
        if value in SUPPORTED_PLATFORMS:
            self.standard_nv_pairs["p"] = value
        else:
            raise RuntimeError(value + " is not a supported platform")

    @contract
    def set_user_id(self, user_id):
        """
            :param  user_id:        User ID
            :type   user_id:        non_empty_string
        """
        self.standard_nv_pairs["uid"] = user_id

    @contract
    def set_app_id(self, app_id):
        """
            :param  app_id:         App ID
            :type   app_id:         str
        """
        self.standard_nv_pairs["aid"] = app_id

    @contract
    def set_screen_resolution(self, width, height):
        """
            :param  width:          Width of the screen
            :param  height:         Height of the screen
            :type   width:          int,>0
            :type   height:         int,>0
        """
        self.standard_nv_pairs["res"] = "".join([str(width), "x", str(height)])

    @contract
    def set_viewport(self, width, height):
        """
            :param  width:          Width of the viewport
            :param  height:         Height of the viewport
            :type   width:          int,>0
            :type   height:         int,>0
        """
        self.standard_nv_pairs["vp"] = "".join([str(width), "x", str(height)])

    @contract
    def set_color_depth(self, depth):
        """
            :param  depth:          Depth of the color on the screen
            :type   depth:          int
        """
        self.standard_nv_pairs["cd"] = depth

    @contract
    def set_timezone(self, timezone):
        """
            Set timezone for the Tracker object.

            :param  timezone:       Timezone as a string
            :type   timezone:       non_empty_string
        """
        self.standard_nv_pairs["tz"] = timezone

    @contract
    def set_lang(self, lang):
        """
            Set language.

            :param  lang:           Language the application is set to
            :type   lang:           non_empty_string
        """
        self.standard_nv_pairs["lang"] = lang

    """
    Tracking methods
    """

    @contract
    def track(self, pb):
        """
            Called by all tracking events to add the standard name-value pairs
            to the Payload object irrespective of the tracked event.

            :param  pb:              Payload builder
            :type   pb:              payload
        """
        pb.add_dict(self.standard_nv_pairs)
        return self.http_get(pb)

    @contract
    def track_page_view(self, page_url, page_title=None, referrer=None, context=None, tstamp=None):
        """
            :param  page_url:       URL of the viewed page
            :type   page_url:       non_empty_string
            :param  page_title:     Title of the viewed page
            :type   page_title:     string_or_none
            :param  referrer:       Referrer of the page
            :type   referrer:       string_or_none
            :param  context:        Custom context for the event
            :type   context:        dict(str:*) | None
        """
        pb = payload.Payload(tstamp)
        pb.add("e", "pv")           # pv: page view
        pb.add("url", page_url)
        pb.add("page", page_title)
        pb.add("refr", referrer)
        pb.add("evn", DEFAULT_VENDOR)
        pb.add_json(context, self.config["encode_base64"], "cx", "co")
        return self.track(pb)

    @contract
    def track_ecommerce_transaction(self, order_id, tr_total_value,
                                    tr_affiliation=None, tr_tax_value=None, tr_shipping=None,
                                    tr_city=None, tr_state=None, tr_country=None, tr_currency=None,
                                    context=None,
                                    tstamp=None):
        """
            :param  order_id:       ID of the eCommerce transaction
            :type   order_id:       non_empty_string
            :param  tr_total_value: Total transaction value
            :type   tr_total_value: int | float
            :param  tr_affiliation: Transaction affiliation
            :type   tr_affiliation: string_or_none
            :param  tr_tax_value:   Transaction tax value
            :type   tr_tax_value:   int | float | None
            :param  tr_shipping:    Delivery cost charged
            :type   tr_shipping:    int | float | None
            :param  tr_city:        Delivery address city
            :type   tr_city:        string_or_none
            :param  tr_state:       Delivery address state
            :type   tr_state:       string_or_none
            :param  tr_country:     Delivery address country
            :type   tr_country:     string_or_none
            :param  tr_currency:    The currency the price is expressed in
            :type   tr_currency:    string_or_none
            :param  context:        Custom context for the event
            :type   context:        dict(str:*) | None
        """
        pb = payload.Payload(tstamp)
        pb.add("e", "tr")
        pb.add("tr_id", order_id)
        pb.add("tr_af", tr_affiliation)
        pb.add("tr_tt", tr_total_value)
        pb.add("tr_tx", tr_tax_value)
        pb.add("tr_sh", tr_shipping)
        pb.add("tr_ci", tr_city)
        pb.add("tr_st", tr_state)
        pb.add("tr_co", tr_country)
        pb.add("evn", DEFAULT_VENDOR)
        pb.add_json(context, self.config["encode_base64"], "cx", "co")
        return self.track(pb)

    @contract
    def track_ecommerce_transaction_item(self, ti_id, ti_sku, ti_price, ti_quantity,
                                         ti_name=None, ti_category=None, tr_currency=None,
                                         context=None,
                                         tstamp=None):
        """
            :param  ti_id:          Order ID
            :type   ti_id:          non_empty_string
            :param  ti_sku:         Item SKU
            :type   ti_sku:         non_empty_string
            :param  ti_price:       Item price
            :type   ti_price:       int | float
            :param  ti_quantity:    Item quantity
            :type   ti_quantity:    int
            :param  ti_name:        Item name
            :type   ti_name:        string_or_none
            :param  ti_category:    Item category
            :type   ti_category:    string_or_none
            :param  tr_currency:    The currency the price is expressed in
            :type   tr_currency:    string_or_none
            :param  context:        Custom context for the event
            :type   context:        dict(str:*) | None
        """
        pb = payload.Payload(tstamp)
        pb.add("e", "ti")
        pb.add("ti_id", ti_id)
        pb.add("ti_sk", ti_sku)
        pb.add("ti_nm", ti_name)
        pb.add("ti_ca", ti_category)
        pb.add("ti_pr", ti_price)
        pb.add("ti_qu", ti_quantity)
        pb.add("evn", DEFAULT_VENDOR)
        pb.add_json(context, self.config["encode_base64"], "cx", "co")
        return self.track(pb)

    @contract
    def track_screen_view(self, name, id_=None, context=None, tstamp=None):
        """
            :param  name:           The name of the screen view event
            :type   name:           non_empty_string
            :param  id_:            Screen view ID
            :type   id_:            string_or_none
            :param  context:        Custom context for the event
            :type   context:        dict(str:*) | None
        """
        return self.track_unstruct_event("screen_view", {"name": name, "id": id_}, DEFAULT_VENDOR, context, tstamp)

    @contract
    def track_struct_event(self, category, action, label=None, property_=None, value=None,
                           context=None,
                           tstamp=None):
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
            :param  context:        Custom context for the event
            :type   context:        dict(str:*) | None
        """
        pb = payload.Payload(tstamp)
        pb.add("e", "se")
        pb.add("se_ca", category)
        pb.add("se_ac", action)
        pb.add("se_la", label)
        pb.add("se_pr", property_)
        pb.add("se_va", value)
        pb.add("evn", DEFAULT_VENDOR)
        pb.add_json(context, self.config["encode_base64"], "cx", "co")
        return self.track(pb)

    @contract
    def track_unstruct_event(self, event_name, dict_, event_vendor=None, context=None, tstamp=None):
        """
            :param  event_name:      The name of the event
            :type   event_name:      non_empty_string
            :param  dict_:           The properties of the event
            :type   dict_:           dict(str:*)
            :param  event_vendor:    The author of the event
            :type   event_vendor:    string_or_none
            :param  context:        Custom context for the event
            :type   context:        dict(str:*) | None
        """
        pb = payload.Payload(tstamp)

        pb.add("e", "ue")
        pb.add("ue_na", event_name)
        pb.add_unstruct(dict_, self.config["encode_base64"], "ue_px", "ue_pr")
        pb.add("evn", event_vendor)
        pb.add_json(context, self.config["encode_base64"], "cx", "co")
        return self.track(pb)
