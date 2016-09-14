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
import uuid
import six

from contracts import contract, new_contract

from snowplow_tracker import payload, _version, SelfDescribingJson
from snowplow_tracker import subject as _subject
from snowplow_tracker.timestamp import Timestamp, TrueTimestamp, DeviceTimestamp


"""
Constants & config
"""

VERSION = "py-%s" % _version.__version__
DEFAULT_ENCODE_BASE64 = True
BASE_SCHEMA_PATH = "iglu:com.snowplowanalytics.snowplow"
SCHEMA_TAG = "jsonschema"
CONTEXT_SCHEMA = "%s/contexts/%s/1-0-1" % (BASE_SCHEMA_PATH, SCHEMA_TAG)
UNSTRUCT_EVENT_SCHEMA = "%s/unstruct_event/%s/1-0-0" % (BASE_SCHEMA_PATH, SCHEMA_TAG)
FORM_NODE_NAMES = ("INPUT", "TEXTAREA", "SELECT")
FORM_TYPES = (
    "button", "checkbox", "color", "date", "datetime",
    "datetime-local", "email", "file", "hidden", "image", "month",
    "number", "password", "radio", "range", "reset", "search",
    "submit", "tel", "text", "time", "url", "week"
)

"""
Tracker class
"""


class Tracker:

    new_contract("not_none", lambda s: s is not None)

    new_contract("non_empty_string", lambda s: isinstance(s, six.string_types)
                 and len(s) > 0)
    new_contract("string_or_none", lambda s: (isinstance(s, six.string_types)
                 and len(s) > 0) or s is None)
    new_contract("payload", lambda s: isinstance(s, payload.Payload))

    new_contract("tracker", lambda s: isinstance(s, Tracker))

    new_contract("emitter", lambda s: hasattr(s, "input"))

    new_contract("self_describing_json", lambda s: isinstance(s, SelfDescribingJson))

    new_contract("context_array", "list(self_describing_json)")

    new_contract("form_node_name", lambda s: s in FORM_NODE_NAMES)

    new_contract("form_type", lambda s: s.lower() in FORM_TYPES)

    new_contract("timestamp", lambda x: (isinstance(x, Timestamp)))

    new_contract("form_element", lambda x: Tracker.check_form_element(x))

    @contract
    def __init__(self, emitters, subject=None,
                 namespace=None, app_id=None, encode_base64=DEFAULT_ENCODE_BASE64):
        """
            :param emitters:         Emitters to which events will be sent
            :type  emitters:         list[>0](emitter) | emitter
            :param subject:          Subject to be tracked
            :type  subject:          subject | None
            :param namespace:        Identifier for the Tracker instance
            :type  namespace:        string_or_none
            :param app_id:           Application ID
            :type  app_id:           string_or_none
            :param encode_base64:    Whether JSONs in the payload should be base-64 encoded
            :type  encode_base64:    bool
        """
        if subject is None:
            subject = _subject.Subject()

        if type(emitters) is list:
            self.emitters = emitters
        else:
            self.emitters = [emitters]

        self.subject = subject
        self.encode_base64 = encode_base64

        self.standard_nv_pairs = {
            "tv": VERSION,
            "tna": namespace,
            "aid": app_id
        }
        self.timer = None

    @staticmethod
    @contract
    def get_uuid():
        """
            Set transaction ID for the payload once during the lifetime of the
            event.

            :rtype:           string
        """
        return str(uuid.uuid4())

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
        elif isinstance(tstamp, (int, float, )):
            return int(tstamp)


    """
    Tracking methods
    """

    @contract
    def track(self, pb):
        """
            Send the payload to a emitter

            :param  pb:              Payload builder
            :type   pb:              payload
            :rtype:                  tracker
        """
        for emitter in self.emitters:
            emitter.input(pb.nv_pairs)
        return self

    @contract
    def complete_payload(self, pb, context, tstamp):
        """
            Called by all tracking events to add the standard name-value pairs
            to the Payload object irrespective of the tracked event.

            :param  pb:              Payload builder
            :type   pb:              payload
            :param  context:         Custom context for the event
            :type   context:         context_array | None
            :param  tstamp:          Optional user-provided timestamp for the event
            :type   tstamp:          timestamp | int | float | None
            :rtype:                  tracker
        """
        pb.add("eid", Tracker.get_uuid())

        if isinstance(tstamp, TrueTimestamp):
            pb.add("ttm", tstamp.value)
        if isinstance(tstamp, DeviceTimestamp):
            pb.add("dtm", Tracker.get_timestamp(tstamp.value))
        elif isinstance(tstamp, (int, float, type(None))):
            pb.add("dtm", Tracker.get_timestamp(tstamp))

        if context is not None:
            context_jsons = list(map(lambda c: c.to_json(), context))
            context_envelope = SelfDescribingJson(CONTEXT_SCHEMA, context_jsons).to_json()
            pb.add_json(context_envelope, self.encode_base64, "cx", "co")

        pb.add_dict(self.standard_nv_pairs)

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
            :type   context:        context_array | None
            :param  tstamp:         Optional user-provided timestamp for the event
            :type   tstamp:         timestamp | int | float | None
            :rtype:                 tracker
        """
        pb = payload.Payload()
        pb.add("e", "pv")           # pv: page view
        pb.add("url", page_url)
        pb.add("page", page_title)
        pb.add("refr", referrer)

        return self.complete_payload(pb, context, tstamp)

    @contract
    def track_page_ping(self, page_url, page_title=None, referrer=None, min_x=None, max_x=None, min_y=None, max_y=None, context=None, tstamp=None):
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
            :param  context:        Custom context for the event
            :type   context:        context_array | None
            :param  tstamp:         Optional user-provided timestamp for the event
            :type   tstamp:         timestamp | int | float | None
            :rtype:                 tracker
        """
        pb = payload.Payload()
        pb.add("e", "pp")           # pp: page ping
        pb.add("url", page_url)
        pb.add("page", page_title)
        pb.add("refr", referrer)
        pb.add("pp_mix", min_x)
        pb.add("pp_max", max_x)
        pb.add("pp_miy", min_y)
        pb.add("pp_may", max_y)

        return self.complete_payload(pb, context, tstamp)

    @contract
    def track_link_click(self, target_url, element_id=None,
                         element_classes=None, element_target=None,
                         element_content=None, context=None, tstamp=None):
        """
            :param  target_url:     Target URL of the link
            :type   target_url:     non_empty_string
            :param  element_id:     ID attribute of the HTML element
            :type   element_id:     string_or_none
            :param  element_classes:    Classes of the HTML element
            :type   element_classes:    list(str) | tuple(str,*) | None
            :param  element_content:    The content of the HTML element
            :type   element_content:    string_or_none
            :param  context:        Custom context for the event
            :type   context:        context_array | None
            :param  tstamp:         Optional user-provided timestamp for the event
            :type   tstamp:         timestamp | int | float | None
            :rtype:                 tracker
        """
        properties = {}
        properties["targetUrl"] = target_url
        if element_id is not None:
            properties["elementId"] = element_id
        if element_classes is not None:
            properties["elementClasses"] = element_classes
        if element_target is not None:
            properties["elementTarget"] = element_target
        if element_content is not None:
            properties["elementContent"] = element_content

        event_json = SelfDescribingJson("%s/link_click/%s/1-0-1" % (BASE_SCHEMA_PATH, SCHEMA_TAG), properties)

        return self.track_unstruct_event(event_json, context, tstamp)

    @contract
    def track_add_to_cart(self, sku, quantity, name=None, category=None,
                          unit_price=None, currency=None, context=None,
                          tstamp=None):
        """
            :param  sku:            Item SKU or ID
            :type   sku:            non_empty_string
            :param  quantity:       Number added to cart
            :type   quantity:       int
            :param  name:           Item's name
            :type   name:           string_or_none
            :param  category:       Item's category
            :type   category:       string_or_none
            :param  unit_price:     Item's price
            :type   unit_price:     int | float | None
            :param  currency:       Type of currency the price is in
            :type   currency:       string_or_none
            :param  context:        Custom context for the event
            :type   context:        context_array | None
            :param  tstamp:         Optional user-provided timestamp for the event
            :type   tstamp:         timestamp | int | float | None
            :rtype:                 tracker
        """
        properties = {}
        properties["sku"] = sku
        properties["quantity"] = quantity
        if name is not None:
            properties["name"] = name
        if category is not None:
            properties["category"] = category
        if unit_price is not None:
            properties["unitPrice"] = unit_price
        if currency is not None:
            properties["currency"] = currency

        event_json = SelfDescribingJson("%s/add_to_cart/%s/1-0-0" % (BASE_SCHEMA_PATH, SCHEMA_TAG), properties)

        return self.track_unstruct_event(event_json, context, tstamp)

    @contract
    def track_remove_from_cart(self, sku, quantity, name=None, category=None,
                               unit_price=None, currency=None, context=None,
                               tstamp=None):
        """
            :param  sku:            Item SKU or ID
            :type   sku:            non_empty_string
            :param  quantity:       Number added to cart
            :type   quantity:       int
            :param  name:           Item's name
            :type   name:           string_or_none
            :param  category:       Item's category
            :type   category:       string_or_none
            :param  unit_price:     Item's price
            :type   unit_price:     int | float | None
            :param  currency:       Type of currency the price is in
            :type   currency:       string_or_none
            :param  context:        Custom context for the event
            :type   context:        context_array | None
            :param  tstamp:         Optional user-provided timestamp for the event
            :type   tstamp:         timestamp | int | float | None
            :rtype:                 tracker
        """
        properties = {}
        properties["sku"] = sku
        properties["quantity"] = quantity
        if name is not None:
            properties["name"] = name
        if category is not None:
            properties["category"] = category
        if unit_price is not None:
            properties["unitPrice"] = unit_price
        if currency is not None:
            properties["currency"] = currency

        event_json = SelfDescribingJson("%s/remove_from_cart/%s/1-0-0" % (BASE_SCHEMA_PATH, SCHEMA_TAG), properties)

        return self.track_unstruct_event(event_json, context, tstamp)

    @contract
    def track_form_change(self, form_id, element_id, node_name, value, type_=None,
                          element_classes=None, context=None, tstamp=None):
        """
        :param  form_id:        ID attribute of the HTML form
        :type   form_id:        non_empty_string
        :param  element_id:     ID attribute of the HTML element
        :type   element_id:     string_or_none
        :param  node_name:      Type of input element
        :type   node_name:      form_node_name
        :param  value:          Value of the input element
        :type   value:          string_or_none
        :param  type_:          Type of data the element represents
        :type   type_:          non_empty_string, form_type
        :param  element_classes:    Classes of the HTML element
        :type   element_classes:    list(str) | tuple(str,*) | None
        :param  context:        Custom context for the event
        :type   context:        context_array | None
        :param  tstamp:         Optional user-provided timestamp for the event
        :type   tstamp:         timestamp | int | float | None
        :rtype:                 tracker
        """
        properties = dict()
        properties["formId"] = form_id
        properties["elementId"] = element_id
        properties["nodeName"] = node_name
        properties["value"] = value
        if type_ is not None:
            properties["type"] = type_
        if element_classes is not None:
            properties["elementClasses"] = element_classes

        event_json = SelfDescribingJson("%s/change_form/%s/1-0-0" % (BASE_SCHEMA_PATH, SCHEMA_TAG), properties)

        return self.track_unstruct_event(event_json, context, tstamp)

    @contract
    def track_form_submit(self, form_id, form_classes=None, elements=None,
                          context=None, tstamp=None):
        """
            :param  form_id:        ID attribute of the HTML form
            :type   form_id:        non_empty_string
            :param  form_classes:   Classes of the HTML form
            :type   form_classes:   list(str) | tuple(str,*) | None
            :param  elements:       Classes of the HTML form
            :type   elements:       list(form_element) | None
            :param  context:        Custom context for the event
            :type   context:        context_array | None
            :param  tstamp:         Optional user-provided timestamp for the event
            :type   tstamp:         timestamp | int | float | None
            :rtype:                 tracker
        """

        properties = dict()
        properties['formId'] = form_id
        if form_classes is not None:
            properties['formClasses'] = form_classes
        if elements is not None and len(elements) > 0:
            properties['elements'] = elements

        event_json = SelfDescribingJson("%s/submit_form/%s/1-0-0" % (BASE_SCHEMA_PATH, SCHEMA_TAG), properties)

        return self.track_unstruct_event(event_json, context, tstamp)

    @contract
    def track_site_search(self, terms, filters=None, total_results=None,
                          page_results=None, context=None, tstamp=None):
        """
            :param  terms:          Search terms
            :type   terms:          seq[>=1](str)
            :param  filters:        Filters applied to the search
            :type   filters:        dict(str:str|bool) | None
            :param  total_results:  Total number of results returned
            :type   total_results:  int | None
            :param  page_results:   Total number of pages of results
            :type   page_results:   int | None
            :param  context:        Custom context for the event
            :type   context:        context_array | None
            :param  tstamp:         Optional user-provided timestamp for the event
            :type   tstamp:         timestamp | int | float | None
            :rtype:                 tracker
        """
        properties = {}
        properties["terms"] = terms
        if filters is not None:
            properties["filters"] = filters
        if total_results is not None:
            properties["totalResults"] = total_results
        if page_results is not None:
            properties["pageResults"] = page_results

        event_json = SelfDescribingJson("%s/site_search/%s/1-0-0" % (BASE_SCHEMA_PATH, SCHEMA_TAG), properties)

        return self.track_unstruct_event(event_json, context, tstamp)

    @contract
    def track_ecommerce_transaction_item(self, order_id, sku, price, quantity,
                                         name=None, category=None, currency=None,
                                         context=None,
                                         tstamp=None):
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
            :param  context:     Custom context for the event
            :type   context:     context_array | None
            :rtype:              tracker
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

        return self.complete_payload(pb, context, tstamp)

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
            :type   context:        context_array | None
            :rtype:                 tracker
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

        tstamp = Tracker.get_timestamp(tstamp)

        self.complete_payload(pb, context, tstamp)

        for item in items:
            item["tstamp"] = tstamp
            item["order_id"] = order_id
            item["currency"] = currency
            self.track_ecommerce_transaction_item(**item)

        return self

    @contract
    def track_screen_view(self, name=None, id_=None, context=None, tstamp=None):
        """
            :param  name:           The name of the screen view event
            :type   name:           string_or_none
            :param  id_:            Screen view ID
            :type   id_:            string_or_none
            :param  context:        Custom context for the event
            :type   context:        context_array | None
            :rtype:                 tracker
        """
        screen_view_properties = {}
        if name is not None:
            screen_view_properties["name"] = name
        if id_ is not None:
            screen_view_properties["id"] = id_

        event_json = SelfDescribingJson("%s/screen_view/%s/1-0-0" % (BASE_SCHEMA_PATH, SCHEMA_TAG), screen_view_properties)

        return self.track_unstruct_event(event_json, context, tstamp)

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
            :type   context:        context_array | None
            :rtype:                 tracker
        """
        pb = payload.Payload()
        pb.add("e", "se")
        pb.add("se_ca", category)
        pb.add("se_ac", action)
        pb.add("se_la", label)
        pb.add("se_pr", property_)
        pb.add("se_va", value)

        return self.complete_payload(pb, context, tstamp)

    @contract
    def track_unstruct_event(self, event_json, context=None, tstamp=None):
        """
            :param  event_json:      The properties of the event. Has two field:
                                     A "data" field containing the event properties and
                                     A "schema" field identifying the schema against which the data is validated
            :type   event_json:      self_describing_json
            :param  context:         Custom context for the event
            :type   context:         context_array | None
            :param  tstamp:          User-set timestamp
            :type   tstamp:          timestamp | int | None
            :rtype:                  tracker
        """

        envelope = SelfDescribingJson(UNSTRUCT_EVENT_SCHEMA, event_json.to_json()).to_json()

        pb = payload.Payload()

        pb.add("e", "ue")
        pb.add_json(envelope, self.encode_base64, "ue_px", "ue_pr")

        return self.complete_payload(pb, context, tstamp)

    # Alias
    track_self_describing_event = track_unstruct_event

    @contract
    def flush(self, async=False):
        """
            Flush the emitter

            :param  async:  Whether the flush is done asynchronously. Default is False
            :type   async:  bool
            :rtype:         tracker
        """
        for emitter in self.emitters:
            if async:
                emitter.flush()
            else:
                emitter.sync_flush()
        return self

    @contract
    def set_subject(self, subject):
        """
            Set the subject of the events fired by the tracker

            :param subject: Subject to be tracked
            :type  subject: subject | None
            :rtype:         tracker
        """
        self.subject = subject
        return self

    @contract
    def add_emitter(self, emitter):
        """
            Add a new emitter to which events should be passed

            :param emitter: New emitter
            :type  emitter: emitter
            :rtype:         tracker
        """
        self.emitters.append(emitter)
        return self

    @staticmethod
    def check_form_element(element):
        """
            PyContracts helper method to check that dictionary conforms element
            in sumbit_form and change_form schemas
        """
        all_present = isinstance(element, dict) and 'name' in element and 'value' in element and 'nodeName' in element
        try:
            if element['type'] in FORM_TYPES:
                type_valid = True
            else:
                type_valid = False
        except KeyError:
            type_valid = True
        return all_present and element['nodeName'] in FORM_NODE_NAMES and type_valid
