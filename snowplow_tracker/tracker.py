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

import time
import random
from snowplow_tracker import payload, _version, subject
from contracts import contract, new_contract


"""
Constants & config
"""

VERSION = "py-%s" % _version.__version__
DEFAULT_ENCODE_BASE64 = True
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

    new_contract("tracker", lambda s: isinstance(s, Tracker))

    new_contract("consumer", lambda s: hasattr(s, "input"))

    @contract
    def __init__(self, out_queue, _subject=None,
                 namespace=None, app_id=None, context_vendor=None, encode_base64=DEFAULT_ENCODE_BASE64):
        """
            :param out_queue:        Consumer to which events will be sent
            :type  out_queue:        consumer
            :param _subject:         Subject to be tracked
            :type  _subject:         subject | None
            :param namespace:        Identifier for the Tracker instance
            :type  namespace:        string_or_none
            :param app_id:           Application ID
            :type  app_id:           string_or_none            
            :param context_vendor:   Reversed domain name of the company which defined the custom contexts
            :type  context_vendor:   string_or_none
            :param encode_base64:    Whether JSONs in the payload should be base-64 encoded
            :type  encode_base64:    bool
        """
        if _subject is None:
            _subject = subject.Subject()

        self.out_queue = out_queue
        self.subject = _subject        
        self.encode_base64 = encode_base64
        self.context_vendor = context_vendor

        self.standard_nv_pairs = {
            "tv": VERSION,
            "tna": namespace,
            "aid": app_id
        }


    @staticmethod
    @contract
    def get_transaction_id():
        """
            Set transaction ID for the payload once during the lifetime of the
            event.

            :rtype:           int
        """
        tid = random.randrange(100000, 999999)
        return tid

    @staticmethod
    @contract
    def get_timestamp(tstamp=None):
        """
            :param tstamp:    User-input timestamp or None
            :type  tstamp:    int | float | None
            :rtype:           int
        """
        if tstamp is None:
            return int(time.time() * 1000)
        elif isinstance(tstamp, (int, float)):
            return int(tstamp)


    """
    Tracking methods
    """

    @contract
    def track(self, pb):
        """
            Send the payload to a consumer

            :param  pb:              Payload builder
            :type   pb:              payload
            :rtype:                  tracker | int
        """
        result = self.out_queue.input(pb.nv_pairs)
        if result is not None:
            return result
        else:
            return self

    @contract
    def complete_payload(self, pb):
        """
            Called by all tracking events to add the standard name-value pairs
            to the Payload object irrespective of the tracked event.

            :param  pb:              Payload builder
            :type   pb:              payload
            :rtype:                  tracker | int
        """
        pb.add_dict(self.standard_nv_pairs)
        if "co" in pb.nv_pairs or "cx" in pb.nv_pairs:
            pb.add("cv", self.context_vendor)

        pb.add_dict(self.subject.standard_nv_pairs)

        return self.track(pb)

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
            :type   context:        dict(string:*) | None
            :rtype:                 tracker | int
        """
        pb = payload.Payload()
        pb.add("e", "pv")           # pv: page view
        pb.add("url", page_url)
        pb.add("page", page_title)
        pb.add("refr", referrer)
        pb.add("evn", DEFAULT_VENDOR)

        tid = Tracker.get_transaction_id()
        pb.add("tid", tid)
        dtm = Tracker.get_timestamp(tstamp)
        pb.add("dtm", tstamp)        
        pb.add_json(context, self.encode_base64, "cx", "co")

        return self.complete_payload(pb)

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
            :type   context:        dict(string:*) | None
            :rtype:                 tracker | int
        """
        pb = payload.Payload()
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
        pb.add("dtm", tstamp)
        pb.add_json(context, self.encode_base64, "cx", "co")

        return self.complete_payload(pb)

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
            :type   context:        dict(string:*) | None
            :rtype:                 tracker | dict(string:*)
        """
        pb = payload.Payload()
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

        tid = Tracker.get_transaction_id()
        pb.add("tid", tid)
        dtm = Tracker.get_timestamp(tstamp)
        pb.add("dtm", dtm)
        pb.add_json(context, self.encode_base64, "cx", "co")

        transaction_result = self.complete_payload(pb)

        item_results = []

        for item in items:
            item["tstamp"] = dtm
            item["tid"] = tid
            item["order_id"] = order_id
            item["currency"] = currency
            item_results.append(self.track_ecommerce_transaction_item(**item))
        
        if not isinstance(transaction_result, Tracker):
            return {"transaction_result": transaction_result, "item_results": item_results}
        else:
            return self

    
    @contract
    def track_screen_view(self, name, id_=None, context=None, tstamp=None):
        """
            :param  name:           The name of the screen view event
            :type   name:           non_empty_string
            :param  id_:            Screen view ID
            :type   id_:            string_or_none
            :param  context:        Custom context for the event
            :type   context:        dict(string:*) | None
            :rtype:                 tracker | int
        """
        screen_view_properties = {"name": name}
        if id_ is not None:
            screen_view_properties["id"] = id_
        return self.track_unstruct_event(DEFAULT_VENDOR, "screen_view", screen_view_properties, context, tstamp)

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
            :type   context:        dict(string:*) | None
            :rtype:                 tracker | int
        """
        pb = payload.Payload()
        pb.add("e", "se")
        pb.add("se_ca", category)
        pb.add("se_ac", action)
        pb.add("se_la", label)
        pb.add("se_pr", property_)
        pb.add("se_va", value)
        pb.add("evn", DEFAULT_VENDOR)

        tid = Tracker.get_transaction_id()
        pb.add("tid", tid)
        dtm = Tracker.get_timestamp(tstamp)
        pb.add("dtm", tstamp)
        pb.add_json(context, self.encode_base64, "cx", "co")

        return self.complete_payload(pb)

    @contract
    def track_unstruct_event(self, event_vendor, event_name, dict_, context=None, tstamp=None):
        """
            :param  event_vendor:    The author of the event
            :type   event_vendor:    non_empty_string        
            :param  event_name:      The name of the event
            :type   event_name:      non_empty_string
            :param  dict_:           The properties of the event
            :type   dict_:           dict(string:*)
            :param  context:         Custom context for the event
            :type   context:         dict(string:*) | None
            :rtype:                  tracker | int
        """
        pb = payload.Payload()

        pb.add("e", "ue")
        pb.add("ue_na", event_name)
        pb.add_json(dict_, self.encode_base64, "ue_px", "ue_pr")
        pb.add("evn", event_vendor)

        dtm = Tracker.get_timestamp(tstamp)
        pb.add("dtm", tstamp)
        tid = Tracker.get_transaction_id()
        pb.add("tid", tid)
        pb.add_json(context, self.encode_base64, "cx", "co")

        return self.complete_payload(pb)

    @contract
    def flush(self, async=False):
        """
            Flush the consumer

            :param  async:  Whether the flush is done asynchronously
            :type   async:  bool
            :rtype:         tracker | int
        """
        if async:
            self.out_queue.flush()
            return self
        else:
            return self.out_queue.sync_flush()

    def set_subject(self, subject):
        """
            Set the subject of the events fired by the tracker
        """
        self.subject = subject
