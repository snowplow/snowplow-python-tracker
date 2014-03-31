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

    Authors: Anuj More, Alex Dean
    Copyright: Copyright (c) 2013-2014 Snowplow Analytics Ltd
    License: Apache License Version 2.0
"""

import requests
from snowplow_tracker import payload, _version
from contracts import contract, new_contract


"""
Constants & config
"""

VERSION = "py-%s" % _version.__version__
DEFAULT_ENCODE_BASE64 = True
DEFAULT_PLATFORM = "pc"
SUPPORTED_PLATFORMS = set(["pc", "tv", "mob", "cnsl", "iot"])
HTTP_ERRORS = set(["Host not found", "No address associated with name",
                  "No address associated with hostname", ])


"""
Tracker class
"""


class Tracker:

    new_contract('non_empty_string', lambda s: isinstance(s, str)
                 and len(s) > 0)
    new_contract('string_or_none', lambda s: (isinstance(s, str)
                 and len(s) > 0) or s is None)
    new_contract('payload', lambda s: isinstance(s, payload.Payload))

    def __init__(self, collector_uri, collector_type):
        """
        Constructor
        """
        self.collector_uri = collector_uri
        if collector_type is "cloudfront":
            self.collector_uri = Tracker.new_tracker_for_cf(collector_uri)
        elif collector_type is "custom":
            self.collector_uri = Tracker.new_tracker_for_uri(collector_uri)
        else:
            self.collector_uri = collector_uri

        self.config = {
            "encode_base64":    DEFAULT_ENCODE_BASE64,
            "platform":         DEFAULT_PLATFORM,
            "version":          VERSION,
        }

        self.standard_nv_pairs = {}

    def cloudfront(collector_uri):
        return Tracker(collector_uri, "cloudfront")

    def hostname(collector_uri):
        return Tracker(collector_uri, "custom")

    """
    Methods to create a URL
    """

    def as_collector_uri(host):
        return ''.join(["http://", host, "/i"])

    def collector_uri_from_cf(cf_subdomain):
        host = ''.join([cf_subdomain, ".cloudfront.net"])
        return Tracker.as_collector_uri(host)

    @contract
    def new_tracker_for_uri(host):
        """
            Converts a domain name tst.example.com to http://tst.example.com/i

            :param  host:           Custom server hostname
            :type   host:           non_empty_string
            :rtype:                 non_empty_string
        """
        return Tracker.as_collector_uri(host)

    @contract
    def new_tracker_for_cf(cf_subdomain):
        """
            Converts a subdomain abc1234 to http://abc1234.cloudfront.net/i

            :param  cf_subdomain:   Cloudfront subdomain
            :type   cf_subdomain:   non_empty_string
            :rtype:                 non_empty_string
        """
        return Tracker.collector_uri_from_cf(cf_subdomain)

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
            :rtype:                 str | bool
        """

        r = requests.get(self.collector_uri, params=payload.context)
        code = r.status_code
        if code < 0 or code > 600:
            return ''.join(["Unrecognised status code [", str(code), "]"])
        elif code >= 400 and code < 500:
            return ''.join(["HTTP status code [", str(code),
                            "] is a client error"])
        elif code >= 500:
            return ''.join(["HTTP status code [", str(code),
                            "] is a server error"])
        return True

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
            self.config["platform"] = value
        else:
            raise RuntimeError(value + " is not a supported platform")

    @contract
    def set_user_id(self, user_id):
        """
            :param  user_id:        User ID
            :type   user_id:        str
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
        self.standard_nv_pairs["res"] = ''.join([str(width), "x", str(height)])

    @contract
    def set_viewport(self, width, height):
        """
            :param  width:          Width of the viewport
            :param  height:         Height of the viewport
            :type   width:          int,>0
            :type   height:         int,>0
        """
        self.standard_nv_pairs["vp"] = ''.join([str(width), "x", str(height)])

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

            :param  pb:             Payload builder
            :type   pb:             payload
            :rtype:                 str | bool
        """
        pb.add_dict(self.standard_nv_pairs)
        return self.http_get(pb)

    @contract
    def track_page_view(self, page_url, page_title, referrer, tstamp=None):
        """
            :param  page_url:       URL of the viewed page
            :type   page_url:       non_empty_string
            :param  page_title:     Title of the viewed page
            :type   page_title:     non_empty_string
            :param  referrer:       Referrer of the page
            :type   referrer:       string_or_none
        """
        pb = payload.Payload(tstamp)
        pb.add("e", "pv")           # pv: page view
        pb.add("url", page_url)
        pb.add("page", page_title)
        pb.add("refr", referrer)
        return self.track(pb)

    @contract
    def track_ecommerce_transaction(self, order_id, tr_affiliation,
                                    tr_total_value, tr_tax_value, tr_shipping,
                                    tr_city, tr_state, tr_country,
                                    tstamp=None):
        """
            :param  order_id:       ID of the eCommerce transaction
            :type   order_id:       non_empty_string
            :param  tr_affiliation: Transaction affiliation
            :type   tr_affiliation: string_or_none
            :param  tr_total_value: Total transaction value
            :type   tr_total_value: int | float
            :param  tr_tax_value:   Transaction tax value
            :type   tr_tax_value:   int | float
            :param  tr_shipping:    Delivery cost charged
            :type   tr_shipping:    int | float
            :param  tr_city:        Delivery address city
            :type   tr_city:        string_or_none
            :param  tr_state:       Delivery address state
            :type   tr_state:       string_or_none
            :param  tr_country:     Delivery address country
            :type   tr_country:     string_or_none
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
        return self.track(pb)

    @contract
    def track_ecommerce_transaction_item(self, ti_id, ti_sku, ti_name,
                                         ti_category, ti_price, ti_quantity,
                                         tstamp=None):
        """
            :param  ti_id:          Order ID
            :type   ti_id:          non_empty_string
            :param  ti_sku:         Item SKU
            :type   ti_sku:         non_empty_string
            :param  ti_name:        Item name
            :type   ti_name:        non_empty_string
            :param  ti_category:    Item category
            :type   ti_category:    non_empty_string
            :param  ti_price:       Item price
            :type   ti_price:       int | float
            :param  ti_quantity:    Item quantity
            :type   ti_quantity:    int
        """
        pb = payload.Payload(tstamp)
        pb.add("e", "ti")
        pb.add("ti_id", ti_id)
        pb.add("ti_sk", ti_sku)
        pb.add("ti_nm", ti_name)
        pb.add("ti_ca", ti_category)
        pb.add("ti_pr", ti_price)
        pb.add("ti_qu", ti_quantity)
        return self.track(pb)

    @contract
    def track_screen_view(self, name, id_, tstamp=None):
        """
            This function is not a part of the protocol. Undocumented.

            :type   name:           non_empty_string
            :type   id_:            non_empty_string
        """
        pb = payload.Payload(tstamp)
        # Payload has value of "e" set to "sv" for screenviews
        pb.add("e", "sv")
        pb.add("sv_na", name)
        pb.add("sv_id", id_)
        return self.track(pb)

    @contract
    def track_struct_event(self, category, action, label, property_, value,
                           tstamp=None):
        """
            :param  category:       Category of the event
            :type   category:       non_empty_string
            :param  action:         The event itself
            :type   action:         non_empty_string
            :param  label:          Refer to the object the action is
                                    performed on
            :type   label:          non_empty_string
            :param  property_:      Property associated with either the action
                                    or the object
            :type   property_:      non_empty_string
            :param  value:          A value associated with the user action
            :type   value:          int | float
        """
        pb = payload.Payload(tstamp)
        pb.add("e", "se")
        pb.add("se_ca", category)
        pb.add("se_ac", action)
        pb.add("se_la", label)
        pb.add("se_pr", property_)
        pb.add("se_va", value)
        return self.track(pb)

    @contract
    def track_unstruct_event(self, event_name, dict_, tstamp=None):
        """
            :param  event_name:     The name of the event
            :type   event_name:     non_empty_string
            :param  dict_:          The properties of the event
            :type   dict_:          dict(str:*)
        """
        pb = payload.Payload(tstamp)

        pb.add("e", "ue")
        pb.add("ue_na", event_name)
        pb.add_unstruct(dict_, self.config["encode_base64"], "ue_px", "ue_pr")

        return self.track(pb)
