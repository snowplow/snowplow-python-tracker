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
import time
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
HTTP_ERRORS = {"host not found",
               "No address associated with name",
               "No address associated with hostname"}


"""
Tracker class
"""

class Tracker:

    new_contract("non_empty_string", lambda s: isinstance(s, str)
                 and len(s) > 0)
    new_contract("string_or_none", lambda s: (isinstance(s, str)
                 and len(s) > 0) or s is None)
    new_contract("payload", lambda s: isinstance(s, payload.Payload))

    def __init__(self, collector_uri, 
                 namespace=None, app_id=None, context_vendor=None, encode_base64=DEFAULT_ENCODE_BASE64, contracts=True):
        """
        Constructor
        """
        if not contracts:
            disable_all()

        self.collector_uri = self.as_collector_uri(collector_uri)

        self.config = {
            "encode_base64":    encode_base64,
            "context_vendor": context_vendor
        }

        self.standard_nv_pairs = {
            "p": DEFAULT_PLATFORM,
            "tv": VERSION,
            "tna": namespace,
            "aid": app_id
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
            :rtype:                 tuple(bool, int | str)
        """

        r = requests.get(self.collector_uri, params=payload.context)
        code = r.status_code
        if code in HTTP_ERRORS:
            return (False, "Host [" + r.url + "] not found (possible connectivity error)")
        elif code < 0 or code >= 400:
            return (False, code)
        else:
            return (True, code)

    """
    Setter methods
    """

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
            :rtype:                  tuple(bool, int | str)
        """
        pb.add_dict(self.standard_nv_pairs)
        if "co" in pb.context or "cx" in pb.context:
            pb.add("cv", self.config["context_vendor"])
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
            :rtype:                 tuple(bool, int | str)
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
    def track_ecommerce_transaction_item(self, order_id, sku, price, quantity,
                                         name=None, category=None, currency=None,
                                         context=None,
                                         tstamp=None, tid=None):
        """
            This is an internal method called by track_ecommerce_transaction.
            It is not for public use.

            :param  order_id:    Order ID
            :type   order_id:    non_empty_string
            :param  sku:         Item SKU
            :type   sku:         non_empty_string
            :param  price:       Item price
            :type   price:       int | float
            :param  quantity:    Item quantity
            :type   quantity:    int
            :param  name:        Item name
            :type   name:        string_or_none
            :param  category:    Item category
            :type   category:    string_or_none
            :param  currency:    The currency the price is expressed in
            :type   currency:    string_or_none
            :param  context:        Custom context for the event
            :type   context:        dict(str:*) | None
            :rtype:                 tuple(bool, int | str)
        """
        pb = payload.Payload(tstamp)
        pb.add("e", "ti")
        pb.add("ti_id", order_id)
        pb.add("ti_sk", sku)
        pb.add("ti_nm", name)
        pb.add("ti_ca", category)
        pb.add("ti_pr", price)
        pb.add("ti_qu", quantity)
        pb.add("ti_cu", currency)
        pb.add("evn", DEFAULT_VENDOR)
        pb.add("tid", tid)
        pb.add_json(context, self.config["encode_base64"], "cx", "co")
        return self.track(pb)

    @contract
    def track_ecommerce_transaction(self, order_id, total_value,
                          affiliation=None, tax_value=None, shipping=None,
                          city=None, state=None, country=None,  currency=None,
                          items=None,
                          context=None, tstamp=None):
        """
            :param  order_id:       ID of the eCommerce transaction
            :type   order_id:       non_empty_string
            :param  total_value: Total transaction value
            :type   total_value: int | float
            :param  affiliation: Transaction affiliation
            :type   affiliation: string_or_none
            :param  tax_value:   Transaction tax value
            :type   tax_value:   int | float | None
            :param  shipping:    Delivery cost charged
            :type   shipping:    int | float | None
            :param  city:        Delivery address city
            :type   city:        string_or_none
            :param  state:       Delivery address state
            :type   state:       string_or_none
            :param  country:     Delivery address country
            :type   country:     string_or_none
            :param  currency:    The currency the price is expressed in
            :type   currency:    string_or_none
            :param  items:          The items in the transaction
            :type   items:          list(dict(str:*))
            :param  context:        Custom context for the event
            :type   context:        dict(str:*) | None
            :rtype:                 dict(str: tuple(bool, int | str) | list(tuple(bool, int | str)))
        """
        if tstamp is None:
            tstamp = time.time()
        if tstamp and isinstance(tstamp, (int, float)):
            tstamp = int(tstamp * 1000)

        tid = payload.Payload.set_transaction_id()

        pb = payload.Payload(tstamp)
        pb.add("e", "tr")
        pb.add("tr_id", order_id)
        pb.add("tr_tt", total_value)
        pb.add("tr_af", affiliation)
        pb.add("tr_tx", tax_value)
        pb.add("tr_sh", shipping)
        pb.add("tr_ci", city)
        pb.add("tr_st", state)
        pb.add("tr_co", country)
        pb.add("tr_cu", currency)
        pb.add("evn", DEFAULT_VENDOR)
        pb.add("tid", tid)
        pb.add("dtm", tstamp)
        pb.add_json(context, self.config["encode_base64"], "cx", "co")

        transaction_result = self.track(pb)

        item_results = []

        for item in items:
            item["tstamp"] = str(tstamp)
            item["tid"] = tid
            item["order_id"] = order_id
            item["currency"] = currency
            item_results.append(self.track_ecommerce_transaction_item(**item))
        
        return {"transaction_result": transaction_result, "item_results": item_results}
    
    @contract
    def track_screen_view(self, name, id_=None, context=None, tstamp=None):
        """
            :param  name:           The name of the screen view event
            :type   name:           non_empty_string
            :param  id_:            Screen view ID
            :type   id_:            string_or_none
            :param  context:        Custom context for the event
            :type   context:        dict(str:*) | None
            :rtype:                 tuple(bool, int | str)
        """
        screen_view_properties = {"name": name}
        if id_ is not None:
            screen_view_properties["id"] = id_
        return self.track_unstruct_event("screen_view", screen_view_properties, DEFAULT_VENDOR, context, tstamp)

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
            :rtype:                 tuple(bool, int | str)
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
            :rtype:                 tuple(bool, int | str)
        """
        pb = payload.Payload(tstamp)

        pb.add("e", "ue")
        pb.add("ue_na", event_name)
        pb.add_unstruct(dict_, self.config["encode_base64"], "ue_px", "ue_pr")
        pb.add("evn", event_vendor)
        pb.add_json(context, self.config["encode_base64"], "cx", "co")
        return self.track(pb)
