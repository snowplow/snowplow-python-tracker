# """
#     tracker.py

#     Copyright (c) 2013-2022 Snowplow Analytics Ltd. All rights reserved.

#     This program is licensed to you under the Apache License Version 2.0,
#     and you may not use this file except in compliance with the Apache License
#     Version 2.0. You may obtain a copy of the Apache License Version 2.0 at
#     http://www.apache.org/licenses/LICENSE-2.0.

#     Unless required by applicable law or agreed to in writing,
#     software distributed under the Apache License Version 2.0 is distributed on
#     an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#     express or implied. See the Apache License Version 2.0 for the specific
#     language governing permissions and limitations there under.

#     Authors: Anuj More, Alex Dean, Fred Blundun, Paul Boocock
#     Copyright: Copyright (c) 2013-2022 Snowplow Analytics Ltd
#     License: Apache License Version 2.0
# """

import time
import uuid
from typing import Any, Optional, Union, List, Dict, Sequence

from snowplow_tracker import payload, _version, SelfDescribingJson
from snowplow_tracker import subject as _subject
from snowplow_tracker.contracts import non_empty_string, one_of, non_empty, form_element
from snowplow_tracker.typing import JsonEncoderFunction, EmitterProtocol,\
    FORM_NODE_NAMES, FORM_TYPES, FormNodeName, ElementClasses, FormClasses

"""
Constants & config
"""

VERSION = "py-%s" % _version.__version__
DEFAULT_ENCODE_BASE64 = True
BASE_SCHEMA_PATH = "iglu:com.snowplowanalytics.snowplow"
SCHEMA_TAG = "jsonschema"
CONTEXT_SCHEMA = "%s/contexts/%s/1-0-1" % (BASE_SCHEMA_PATH, SCHEMA_TAG)
UNSTRUCT_EVENT_SCHEMA = "%s/unstruct_event/%s/1-0-0" % (BASE_SCHEMA_PATH, SCHEMA_TAG)
ContextArray = List[SelfDescribingJson]

"""
Tracker class
"""


class Tracker:

    def __init__(
            self,
            emitters: Union[List[EmitterProtocol], EmitterProtocol],
            subject: Optional[_subject.Subject] = None,
            namespace: Optional[str] = None,
            app_id: Optional[str] = None,
            encode_base64: bool = DEFAULT_ENCODE_BASE64,
            json_encoder: Optional[JsonEncoderFunction] = None) -> None:
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
            :param json_encoder:     Custom JSON serializer that gets called on non-serializable object
            :type  json_encoder:     function | None
        """
        if subject is None:
            subject = _subject.Subject()

        if type(emitters) is list:
            non_empty(emitters)
            self.emitters = emitters
        else:
            self.emitters = [emitters]

        self.subject = subject
        self.encode_base64 = encode_base64
        self.json_encoder = json_encoder

        self.standard_nv_pairs = {
            "tv": VERSION,
            "tna": namespace,
            "aid": app_id
        }
        self.timer = None

    @staticmethod
    def get_uuid() -> str:
        """
            Set transaction ID for the payload once during the lifetime of the
            event.

            :rtype:           string
        """
        return str(uuid.uuid4())

    @staticmethod
    def get_timestamp(tstamp: Optional[float] = None) -> int:
        """
            :param tstamp:    User-input timestamp or None
            :type  tstamp:    int | float | None
            :rtype:           int
        """
        if isinstance(tstamp, (int, float, )):
            return int(tstamp)
        return int(time.time() * 1000)

    """
    Tracking methods
    """

    def track(self, pb: payload.Payload) -> 'Tracker':
        """
            Send the payload to a emitter

            :param  pb:              Payload builder
            :type   pb:              payload
            :rtype:                  tracker
        """
        for emitter in self.emitters:
            emitter.input(pb.nv_pairs)
        return self

    def complete_payload(
            self,
            pb: payload.Payload,
            context: Optional[List[SelfDescribingJson]],
            tstamp: Optional[float],
            event_subject: Optional[_subject.Subject]) -> 'Tracker':
        """
            Called by all tracking events to add the standard name-value pairs
            to the Payload object irrespective of the tracked event.

            :param  pb:              Payload builder
            :type   pb:              payload
            :param  context:         Custom context for the event
            :type   context:         context_array | None
            :param  tstamp:          Optional event timestamp in milliseconds
            :type   tstamp:          int | float | None
            :param  event_subject:   Optional per event subject
            :type   event_subject:   subject | None
            :rtype:                  tracker
        """
        pb.add("eid", Tracker.get_uuid())

        pb.add("dtm", Tracker.get_timestamp())
        if tstamp is not None:
            pb.add("ttm", Tracker.get_timestamp(tstamp))

        if context is not None:
            context_jsons = list(map(lambda c: c.to_json(), context))
            context_envelope = SelfDescribingJson(CONTEXT_SCHEMA, context_jsons).to_json()
            pb.add_json(context_envelope, self.encode_base64, "cx", "co", self.json_encoder)

        pb.add_dict(self.standard_nv_pairs)

        fin_subject = event_subject if event_subject is not None else self.subject
        pb.add_dict(fin_subject.standard_nv_pairs)

        return self.track(pb)

    def track_page_view(
            self,
            page_url: str,
            page_title: Optional[str] = None,
            referrer: Optional[str] = None,
            context: Optional[List[SelfDescribingJson]] = None,
            tstamp: Optional[float] = None,
            event_subject: Optional[_subject.Subject] = None) -> 'Tracker':
        """
            :param  page_url:       URL of the viewed page
            :type   page_url:       non_empty_string
            :param  page_title:     Title of the viewed page
            :type   page_title:     string_or_none
            :param  referrer:       Referrer of the page
            :type   referrer:       string_or_none
            :param  context:        Custom context for the event
            :type   context:        context_array | None
            :param  tstamp:         Optional event timestamp in milliseconds
            :type   tstamp:         int | float | None
            :param  event_subject:  Optional per event subject
            :type   event_subject:  subject | None
            :rtype:                 tracker
        """
        non_empty_string(page_url)

        pb = payload.Payload()
        pb.add("e", "pv")           # pv: page view
        pb.add("url", page_url)
        pb.add("page", page_title)
        pb.add("refr", referrer)

        return self.complete_payload(pb, context, tstamp, event_subject)

    def track_page_ping(
            self,
            page_url: str,
            page_title: Optional[str] = None,
            referrer: Optional[str] = None,
            min_x: Optional[int] = None,
            max_x: Optional[int] = None,
            min_y: Optional[int] = None,
            max_y: Optional[int] = None,
            context: Optional[List[SelfDescribingJson]] = None,
            tstamp: Optional[float] = None,
            event_subject: Optional[_subject.Subject] = None) -> 'Tracker':
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
            :param  tstamp:         Optional event timestamp in milliseconds
            :type   tstamp:         int | float | None
            :param  event_subject:  Optional per event subject
            :type   event_subject:  subject | None
            :rtype:                 tracker
        """
        non_empty_string(page_url)

        pb = payload.Payload()
        pb.add("e", "pp")           # pp: page ping
        pb.add("url", page_url)
        pb.add("page", page_title)
        pb.add("refr", referrer)
        pb.add("pp_mix", min_x)
        pb.add("pp_max", max_x)
        pb.add("pp_miy", min_y)
        pb.add("pp_may", max_y)

        return self.complete_payload(pb, context, tstamp, event_subject)

    def track_link_click(
            self,
            target_url: str,
            element_id: Optional[str] = None,
            element_classes: Optional[ElementClasses] = None,
            element_target: Optional[str] = None,
            element_content: Optional[str] = None,
            context: Optional[List[SelfDescribingJson]] = None,
            tstamp: Optional[float] = None,
            event_subject: Optional[_subject.Subject] = None) -> 'Tracker':
        """
            :param  target_url:     Target URL of the link
            :type   target_url:     non_empty_string
            :param  element_id:     ID attribute of the HTML element
            :type   element_id:     string_or_none
            :param  element_classes:    Classes of the HTML element
            :type   element_classes:    list(str) | tuple(str,\*) | None
            :param  element_target:     ID attribute of the HTML element
            :type   element_target:     string_or_none
            :param  element_content:    The content of the HTML element
            :type   element_content:    string_or_none
            :param  context:        Custom context for the event
            :type   context:        context_array | None
            :param  tstamp:         Optional event timestamp in milliseconds
            :type   tstamp:         int | float | None
            :param  event_subject:  Optional per event subject
            :type   event_subject:  subject | None
            :rtype:                 tracker
        """
        non_empty_string(target_url)

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

        return self.track_unstruct_event(event_json, context, tstamp, event_subject)

    def track_add_to_cart(
            self,
            sku: str,
            quantity: int,
            name: Optional[str] = None,
            category: Optional[str] = None,
            unit_price: Optional[float] = None,
            currency: Optional[str] = None,
            context: Optional[List[SelfDescribingJson]] = None,
            tstamp: Optional[float] = None,
            event_subject: Optional[_subject.Subject] = None) -> 'Tracker':
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
            :param  tstamp:         Optional event timestamp in milliseconds
            :type   tstamp:         int | float | None
            :param  event_subject:  Optional per event subject
            :type   event_subject:  subject | None
            :rtype:                 tracker
        """
        non_empty_string(sku)

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

        return self.track_unstruct_event(event_json, context, tstamp, event_subject)

    def track_remove_from_cart(
            self,
            sku: str,
            quantity: int,
            name: Optional[str] = None,
            category: Optional[str] = None,
            unit_price: Optional[float] = None,
            currency: Optional[str] = None,
            context: Optional[List[SelfDescribingJson]] = None,
            tstamp: Optional[float] = None,
            event_subject: Optional[_subject.Subject] = None) -> 'Tracker':
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
            :param  tstamp:         Optional event timestamp in milliseconds
            :type   tstamp:         int | float | None
            :param  event_subject:  Optional per event subject
            :type   event_subject:  subject | None
            :rtype:                 tracker
        """
        non_empty_string(sku)

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

        return self.track_unstruct_event(event_json, context, tstamp, event_subject)

    def track_form_change(
            self,
            form_id: str,
            element_id: Optional[str],
            node_name: FormNodeName,
            value: Optional[str],
            type_: Optional[str] = None,
            element_classes: Optional[ElementClasses] = None,
            context: Optional[List[SelfDescribingJson]] = None,
            tstamp: Optional[float] = None,
            event_subject: Optional[_subject.Subject] = None) -> 'Tracker':
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
            :type   element_classes:    list(str) | tuple(str,\*) | None
            :param  context:        Custom context for the event
            :type   context:        context_array | None
            :param  tstamp:         Optional event timestamp in milliseconds
            :type   tstamp:         int | float | None
            :param  event_subject:  Optional per event subject
            :type   event_subject:  subject | None
            :rtype:                 tracker
        """
        non_empty_string(form_id)
        one_of(node_name, FORM_NODE_NAMES)
        if type_ is not None:
            one_of(type_.lower(), FORM_TYPES)

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

        return self.track_unstruct_event(event_json, context, tstamp, event_subject)

    def track_form_submit(
            self,
            form_id: str,
            form_classes: Optional[FormClasses] = None,
            elements: Optional[List[Dict[str, Any]]] = None,
            context: Optional[List[SelfDescribingJson]] = None,
            tstamp: Optional[float] = None,
            event_subject: Optional[_subject.Subject] = None) -> 'Tracker':
        """
            :param  form_id:        ID attribute of the HTML form
            :type   form_id:        non_empty_string
            :param  form_classes:   Classes of the HTML form
            :type   form_classes:   list(str) | tuple(str,\*) | None
            :param  elements:       Classes of the HTML form
            :type   elements:       list(form_element) | None
            :param  context:        Custom context for the event
            :type   context:        context_array | None
            :param  tstamp:         Optional event timestamp in milliseconds
            :type   tstamp:         int | float | None
            :param  event_subject:  Optional per event subject
            :type   event_subject:  subject | None
            :rtype:                 tracker
        """
        non_empty_string(form_id)
        for element in elements or []:
            form_element(element)

        properties = dict()
        properties['formId'] = form_id
        if form_classes is not None:
            properties['formClasses'] = form_classes
        if elements is not None and len(elements) > 0:
            properties['elements'] = elements

        event_json = SelfDescribingJson("%s/submit_form/%s/1-0-0" % (BASE_SCHEMA_PATH, SCHEMA_TAG), properties)

        return self.track_unstruct_event(event_json, context, tstamp, event_subject)

    def track_site_search(
            self,
            terms: Sequence[str],
            filters: Optional[Dict[str, Union[str, bool]]] = None,
            total_results: Optional[int] = None,
            page_results: Optional[int] = None,
            context: Optional[List[SelfDescribingJson]] = None,
            tstamp: Optional[float] = None,
            event_subject: Optional[_subject.Subject] = None) -> 'Tracker':
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
            :param  tstamp:         Optional event timestamp in milliseconds
            :type   tstamp:         int | float | None
            :param  event_subject:  Optional per event subject
            :type   event_subject:  subject | None
            :rtype:                 tracker
        """
        non_empty(terms)

        properties = {}
        properties["terms"] = terms
        if filters is not None:
            properties["filters"] = filters
        if total_results is not None:
            properties["totalResults"] = total_results
        if page_results is not None:
            properties["pageResults"] = page_results

        event_json = SelfDescribingJson("%s/site_search/%s/1-0-0" % (BASE_SCHEMA_PATH, SCHEMA_TAG), properties)

        return self.track_unstruct_event(event_json, context, tstamp, event_subject)

    def track_ecommerce_transaction_item(
            self,
            order_id: str,
            sku: str,
            price: float,
            quantity: int,
            name: Optional[str] = None,
            category: Optional[str] = None,
            currency: Optional[str] = None,
            context: Optional[List[SelfDescribingJson]] = None,
            tstamp: Optional[float] = None,
            event_subject: Optional[_subject.Subject] = None) -> 'Tracker':
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
            :param  tstamp:      Optional event timestamp in milliseconds
            :type   tstamp:      int | float | None
            :param  event_subject:  Optional per event subject
            :type   event_subject:  subject | None
            :rtype:              tracker
        """
        non_empty_string(order_id)
        non_empty_string(sku)

        pb = payload.Payload()
        pb.add("e", "ti")
        pb.add("ti_id", order_id)
        pb.add("ti_sk", sku)
        pb.add("ti_nm", name)
        pb.add("ti_ca", category)
        pb.add("ti_pr", price)
        pb.add("ti_qu", quantity)
        pb.add("ti_cu", currency)

        return self.complete_payload(pb, context, tstamp, event_subject)

    def track_ecommerce_transaction(
            self,
            order_id: str,
            total_value: float,
            affiliation: Optional[str] = None,
            tax_value: Optional[float] = None,
            shipping: Optional[float] = None,
            city: Optional[str] = None,
            state: Optional[str] = None,
            country: Optional[str] = None,
            currency: Optional[str] = None,
            items: Optional[List[Dict[str, Any]]] = None,
            context: Optional[List[SelfDescribingJson]] = None,
            tstamp: Optional[float] = None,
            event_subject: Optional[_subject.Subject] = None) -> 'Tracker':
        """
            :param  order_id:       ID of the eCommerce transaction
            :type   order_id:       non_empty_string
            :param  total_value:    Total transaction value
            :type   total_value:    int | float
            :param  affiliation:    Transaction affiliation
            :type   affiliation:    string_or_none
            :param  tax_value:      Transaction tax value
            :type   tax_value:      int | float | None
            :param  shipping:       Delivery cost charged
            :type   shipping:       int | float | None
            :param  city:           Delivery address city
            :type   city:           string_or_none
            :param  state:          Delivery address state
            :type   state:          string_or_none
            :param  country:        Delivery address country
            :type   country:        string_or_none
            :param  currency:       The currency the price is expressed in
            :type   currency:       string_or_none
            :param  items:          The items in the transaction
            :type   items:          list(dict(str:\*)) | None
            :param  context:        Custom context for the event
            :type   context:        context_array | None
            :param  tstamp:         Optional event timestamp in milliseconds
            :type   tstamp:         int | float | None
            :param  event_subject:  Optional per event subject
            :type   event_subject:  subject | None
            :rtype:                 tracker
        """
        non_empty_string(order_id)

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

        self.complete_payload(pb, context, tstamp, event_subject)

        if items is None:
            items = []
        for item in items:
            item["tstamp"] = tstamp
            item["event_subject"] = event_subject
            item["order_id"] = order_id
            item["currency"] = currency
            self.track_ecommerce_transaction_item(**item)

        return self

    def track_screen_view(
            self,
            name: Optional[str] = None,
            id_: Optional[str] = None,
            context: Optional[List[SelfDescribingJson]] = None,
            tstamp: Optional[float] = None,
            event_subject: Optional[_subject.Subject] = None) -> 'Tracker':
        """
            :param  name:           The name of the screen view event
            :type   name:           string_or_none
            :param  id_:            Screen view ID
            :type   id_:            string_or_none
            :param  context:        Custom context for the event
            :type   context:        context_array | None
            :param  tstamp:         Optional event timestamp in milliseconds
            :type   tstamp:         int | float | None
            :param  event_subject:  Optional per event subject
            :type   event_subject:  subject | None
            :rtype:                 tracker
        """
        screen_view_properties = {}
        if name is not None:
            screen_view_properties["name"] = name
        if id_ is not None:
            screen_view_properties["id"] = id_

        event_json = SelfDescribingJson("%s/screen_view/%s/1-0-0" % (BASE_SCHEMA_PATH, SCHEMA_TAG), screen_view_properties)

        return self.track_unstruct_event(event_json, context, tstamp, event_subject)

    def track_struct_event(
            self,
            category: str,
            action: str,
            label: Optional[str] = None,
            property_: Optional[str] = None,
            value: Optional[float] = None,
            context: Optional[List[SelfDescribingJson]] = None,
            tstamp: Optional[float] = None,
            event_subject: Optional[_subject.Subject] = None) -> 'Tracker':
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
            :param  tstamp:         Optional event timestamp in milliseconds
            :type   tstamp:         int | float | None
            :param  event_subject:  Optional per event subject
            :type   event_subject:  subject | None
            :rtype:                 tracker
        """
        non_empty_string(category)
        non_empty_string(action)

        pb = payload.Payload()
        pb.add("e", "se")
        pb.add("se_ca", category)
        pb.add("se_ac", action)
        pb.add("se_la", label)
        pb.add("se_pr", property_)
        pb.add("se_va", value)

        return self.complete_payload(pb, context, tstamp, event_subject)

    def track_unstruct_event(
            self,
            event_json: SelfDescribingJson,
            context: Optional[List[SelfDescribingJson]] = None,
            tstamp: Optional[float] = None,
            event_subject: Optional[_subject.Subject] = None) -> 'Tracker':
        """
            :param  event_json:      The properties of the event. Has two field:
                                     A "data" field containing the event properties and
                                     A "schema" field identifying the schema against which the data is validated
            :type   event_json:      self_describing_json
            :param  context:         Custom context for the event
            :type   context:         context_array | None
            :param  tstamp:          Optional event timestamp in milliseconds
            :type   tstamp:          int | float | None
            :param  event_subject:   Optional per event subject
            :type   event_subject:   subject | None
            :rtype:                  tracker
        """

        envelope = SelfDescribingJson(UNSTRUCT_EVENT_SCHEMA, event_json.to_json()).to_json()

        pb = payload.Payload()

        pb.add("e", "ue")
        pb.add_json(envelope, self.encode_base64, "ue_px", "ue_pr", self.json_encoder)

        return self.complete_payload(pb, context, tstamp, event_subject)

    # Alias
    track_self_describing_event = track_unstruct_event

    def flush(self, is_async: bool = False) -> 'Tracker':
        """
            Flush the emitter

            :param  is_async:  Whether the flush is done asynchronously. Default is False
            :type   is_async:  bool
            :rtype:         tracker
        """
        for emitter in self.emitters:
            if is_async:
                if hasattr(emitter, 'flush'):
                    emitter.flush()
            else:
                if hasattr(emitter, 'sync_flush'):
                    emitter.sync_flush()
        return self

    def set_subject(self, subject: Optional[_subject.Subject]) -> 'Tracker':
        """
            Set the subject of the events fired by the tracker

            :param subject: Subject to be tracked
            :type  subject: subject | None
            :rtype:         tracker
        """
        self.subject = subject
        return self

    def add_emitter(self, emitter: EmitterProtocol) -> 'Tracker':
        """
            Add a new emitter to which events should be passed

            :param emitter: New emitter
            :type  emitter: emitter
            :rtype:         tracker
        """
        self.emitters.append(emitter)
        return self
