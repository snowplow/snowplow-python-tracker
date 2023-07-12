# """
#     test_tracker.py

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

import re
import json
import unittest
import unittest.mock as mock

from freezegun import freeze_time
from typing import Any, Optional

from snowplow_tracker.contracts import disable_contracts, enable_contracts
from snowplow_tracker.tracker import Tracker
from snowplow_tracker.tracker import VERSION as TRACKER_VERSION
from snowplow_tracker.subject import Subject
from snowplow_tracker.payload import Payload
from snowplow_tracker.self_describing_json import SelfDescribingJson
from snowplow_tracker.events import Event, SelfDescribing, ScreenView

UNSTRUCT_SCHEMA = "iglu:com.snowplowanalytics.snowplow/unstruct_event/jsonschema/1-0-0"
CONTEXT_SCHEMA = "iglu:com.snowplowanalytics.snowplow/contexts/jsonschema/1-0-1"
LINK_CLICK_SCHEMA = "iglu:com.snowplowanalytics.snowplow/link_click/jsonschema/1-0-1"
ADD_TO_CART_SCHEMA = "iglu:com.snowplowanalytics.snowplow/add_to_cart/jsonschema/1-0-0"
REMOVE_FROM_CART_SCHEMA = (
    "iglu:com.snowplowanalytics.snowplow/remove_from_cart/jsonschema/1-0-0"
)
FORM_CHANGE_SCHEMA = "iglu:com.snowplowanalytics.snowplow/change_form/jsonschema/1-0-0"
FORM_SUBMIT_SCHEMA = "iglu:com.snowplowanalytics.snowplow/submit_form/jsonschema/1-0-0"
SITE_SEARCH_SCHEMA = "iglu:com.snowplowanalytics.snowplow/site_search/jsonschema/1-0-0"
MOBILE_SCREEN_VIEW_SCHEMA = (
    "iglu:com.snowplowanalytics.mobile/screen_view/jsonschema/1-0-0"
)
SCREEN_VIEW_SCHEMA = "iglu:com.snowplowanalytics.snowplow/screen_view/jsonschema/1-0-0"

# helpers
_TEST_UUID = "5628c4c6-3f8a-43f8-a09f-6ff68f68dfb6"
geoSchema = "iglu:com.snowplowanalytics.snowplow/geolocation_context/jsonschema/1-0-0"
geoData = {"latitude": -23.2, "longitude": 43.0}
movSchema = "iglu:com.acme_company/movie_poster/jsonschema/2-1-1"
movData = {"movie": "TestMovie", "year": 2021}


def mocked_uuid() -> str:
    return _TEST_UUID


def mocked_track(
    event: Any,
    context: Optional[Any] = None,
    tstamp: Optional[Any] = None,
    event_subject: Optional[Any] = None,
) -> None:
    pass


def mocked_complete_payload(
    event: Any,
    event_subject: Optional[Any],
    context: Optional[Any],
    tstamp: Optional[Any],
) -> Payload:
    pass


def mocked_track_trans_item(*args: Any, **kwargs: Any) -> None:
    pass


def mocked_track_unstruct(*args: Any, **kwargs: Any) -> None:
    pass


class ContractsDisabled(object):
    def __enter__(self) -> None:
        disable_contracts()

    def __exit__(self, type: Any, value: Any, traceback: Any) -> None:
        enable_contracts()


class TestTracker(unittest.TestCase):
    def create_patch(self, name: str) -> Any:
        patcher = mock.patch(name)
        thing = patcher.start()
        thing.side_effect = mock.MagicMock
        self.addCleanup(patcher.stop)
        return thing

    def setUp(self) -> None:
        pass

    def test_initialisation(self) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        t = Tracker("cloudfront", [e], encode_base64=False, app_id="AF003")
        self.assertEqual(t.standard_nv_pairs["tna"], "cloudfront")
        self.assertEqual(t.standard_nv_pairs["aid"], "AF003")
        self.assertEqual(t.encode_base64, False)

    def test_initialisation_default_optional(self) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        t = Tracker("namespace", e)
        self.assertEqual(t.emitters, [e])
        self.assertTrue(t.standard_nv_pairs["aid"] is None)
        self.assertEqual(t.encode_base64, True)

    def test_initialisation_emitter_list(self) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e1 = mokEmitter()
        e2 = mokEmitter()

        t = Tracker("namespace", [e1, e2])
        self.assertEqual(t.emitters, [e1, e2])

    def test_initialisation_error(self) -> None:
        with self.assertRaises(ValueError):
            Tracker("namespace", [])

    def test_initialization_with_subject(self) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        s = Subject()
        t = Tracker("namespace", e, subject=s)
        self.assertIs(t.subject, s)

    def test_get_uuid(self) -> None:
        eid = Tracker.get_uuid()
        self.assertIsNotNone(
            re.match(
                r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z", eid
            )
        )

    @freeze_time("1970-01-01 00:00:01")
    def test_get_timestamp(self) -> None:
        tstamp = Tracker.get_timestamp()
        self.assertEqual(tstamp, 1000)  # 1970-01-01 00:00:01 in ms

    def test_get_timestamp_1(self) -> None:
        tstamp = Tracker.get_timestamp(1399021242030)
        self.assertEqual(tstamp, 1399021242030)

    def test_get_timestamp_2(self) -> None:
        tstamp = Tracker.get_timestamp(1399021242240.0303)
        self.assertEqual(tstamp, 1399021242240)

    @freeze_time("1970-01-01 00:00:01")
    def test_get_timestamp_3(self) -> None:
        tstamp = Tracker.get_timestamp("1399021242030")  # test wrong arg type
        self.assertEqual(tstamp, 1000)  # 1970-01-01 00:00:01 in ms

    @mock.patch("snowplow_tracker.Tracker.track")
    def test_alias_of_track_self_describing_event(self, mok_track: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track.side_effect = mocked_track
        t = Tracker("namespace", e)
        evJson = SelfDescribingJson("test.schema", {"n": "v"})
        # call the alias
        t.track_self_describing_event(evJson)
        self.assertEqual(mok_track.call_count, 1)

    def test_flush(self) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e1 = mokEmitter()
        e2 = mokEmitter()

        t = Tracker("namespace", [e1, e2])
        t.flush()
        e1.flush.assert_not_called()
        self.assertEqual(e1.sync_flush.call_count, 1)
        e2.flush.assert_not_called()
        self.assertEqual(e2.sync_flush.call_count, 1)

    def test_flush_async(self) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e1 = mokEmitter()
        e2 = mokEmitter()

        t = Tracker("namespace", [e1, e2])
        t.flush(is_async=True)
        self.assertEqual(e1.flush.call_count, 1)
        e1.sync_flush.assert_not_called()
        self.assertEqual(e2.flush.call_count, 1)
        e2.sync_flush.assert_not_called()

    def test_set_subject(self) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        t = Tracker("namespace", e)
        new_subject = Subject()
        self.assertIsNot(t.subject, new_subject)
        t.set_subject(new_subject)
        self.assertIs(t.subject, new_subject)

    def test_add_emitter(self) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e1 = mokEmitter()
        e2 = mokEmitter()

        t = Tracker("namespace", e1)
        t.add_emitter(e2)
        self.assertEqual(t.emitters, [e1, e2])

    ###
    # test track and complete payload methods
    ###

    def test_track(self) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e1 = mokEmitter()
        e2 = mokEmitter()
        e3 = mokEmitter()

        t = Tracker("namespace", [e1, e2, e3])

        mok_event = self.create_patch("snowplow_tracker.events.Event")
        t.track(mok_event)
        mok_payload = mok_event.build_payload().nv_pairs

        e1.input.assert_called_once_with(mok_payload)
        e2.input.assert_called_once_with(mok_payload)
        e3.input.assert_called_once_with(mok_payload)

    @freeze_time("2021-04-19 00:00:01")  # unix: 1618790401000
    @mock.patch("snowplow_tracker.Tracker.get_uuid")
    def test_complete_payload(self, mok_uuid: Any) -> None:
        mok_uuid.side_effect = mocked_uuid

        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        t = Tracker("namespace", e)
        s = Subject()
        event = Event(event_subject=s)
        payload = t.complete_payload(event).nv_pairs

        expected = {
            "eid": _TEST_UUID,
            "dtm": 1618790401000,
            "tv": TRACKER_VERSION,
            "p": "pc",
            "tna": "namespace",
        }
        self.assertDictEqual(payload, expected)

    @freeze_time("2021-04-19 00:00:01")  # unix: 1618790401000
    @mock.patch("snowplow_tracker.Tracker.get_uuid")
    def test_complete_payload_tstamp(self, mok_uuid: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_uuid.side_effect = mocked_uuid
        t = Tracker("namespace", e)
        s = Subject()
        time_in_millis = 100010001000
        event = Event(true_timestamp=time_in_millis, event_subject=s)

        payload = t.complete_payload(event=event).nv_pairs

        expected = {
            "tna": "namespace",
            "eid": _TEST_UUID,
            "dtm": 1618790401000,
            "ttm": time_in_millis,
            "tv": TRACKER_VERSION,
            "p": "pc",
        }
        self.assertDictEqual(payload, expected)

    @freeze_time("2021-04-19 00:00:01")  # unix: 1618790401000
    @mock.patch("snowplow_tracker.Tracker.get_uuid")
    def test_complete_payload_co(self, mok_uuid: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_uuid.side_effect = mocked_uuid

        t = Tracker("namespace", e, encode_base64=False)

        geo_ctx = SelfDescribingJson(geoSchema, geoData)
        mov_ctx = SelfDescribingJson(movSchema, movData)
        ctx_array = [geo_ctx, mov_ctx]
        event = Event(context=ctx_array)
        payload = t.complete_payload(event=event).nv_pairs

        expected_co = {
            "schema": CONTEXT_SCHEMA,
            "data": [
                {"schema": geoSchema, "data": geoData},
                {"schema": movSchema, "data": movData},
            ],
        }
        self.assertIn("co", payload)
        self.assertDictEqual(json.loads(payload["co"]), expected_co)

    @freeze_time("2021-04-19 00:00:01")  # unix: 1618790401000
    @mock.patch("snowplow_tracker.Tracker.get_uuid")
    def test_complete_payload_cx(self, mok_uuid: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_uuid.side_effect = mocked_uuid

        t = Tracker("namespace", e, encode_base64=True)

        geo_ctx = SelfDescribingJson(geoSchema, geoData)
        mov_ctx = SelfDescribingJson(movSchema, movData)
        ctx_array = [geo_ctx, mov_ctx]
        event = Event(context=ctx_array)
        payload = t.complete_payload(event=event).nv_pairs

        self.assertIn("cx", payload)

    @freeze_time("2021-04-19 00:00:01")  # unix: 1618790401000
    @mock.patch("snowplow_tracker.Tracker.get_uuid")
    def test_complete_payload_event_subject(self, mok_uuid: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_uuid.side_effect = mocked_uuid

        t = Tracker("namespace", e)
        event_subject = Subject().set_lang("EN").set_user_id("tester")
        event = Event(event_subject=event_subject)
        payload = t.complete_payload(event=event).nv_pairs

        expected = {
            "tna": "namespace",
            "eid": _TEST_UUID,
            "dtm": 1618790401000,
            "tv": TRACKER_VERSION,
            "p": "pc",
            "lang": "EN",
            "uid": "tester",
        }
        self.assertDictEqual(payload, expected)

    ###
    # test track_x methods
    ###

    @mock.patch("snowplow_tracker.Tracker.track")
    def test_track_self_describing_event(self, mok_track: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track.side_effect = mocked_track

        t = Tracker("namespace", e, encode_base64=False)
        event_json = SelfDescribingJson("test.sde.schema", {"n": "v"})
        event = SelfDescribing(event_json=event_json)
        actual_pairs = event.build_payload(
            encode_base64=t.encode_base64,
            json_encoder=t.json_encoder,
        ).nv_pairs

        t.track_self_describing_event(event_json)
        self.assertEqual(mok_track.call_count, 1)

        complete_args_dict = mok_track.call_args_list[0][1]
        self.assertEqual(len(complete_args_dict), 1)

        # payload
        actual_ue_pr = json.loads(actual_pairs["ue_pr"])

        expectedUePr = {
            "data": {"data": {"n": "v"}, "schema": "test.sde.schema"},
            "schema": UNSTRUCT_SCHEMA,
        }

        self.assertDictEqual(actual_ue_pr, expectedUePr)
        self.assertEqual(actual_pairs["e"], "ue")

    @mock.patch("snowplow_tracker.Tracker.track")
    def test_track_self_describing_event_all_args(self, mok_track: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track.side_effect = mocked_track

        t = Tracker("namespace", e, encode_base64=False)
        event_json = SelfDescribingJson("test.schema", {"n": "v"})
        ctx = SelfDescribingJson("test.context.schema", {"user": "tester"})
        event_context = [ctx]
        event_tstamp = 1399021242030

        event = SelfDescribing(event_json=event_json)
        actual_pairs = event.build_payload(
            encode_base64=t.encode_base64,
            json_encoder=t.json_encoder,
        ).nv_pairs

        t.track_self_describing_event(event_json, event_context, event_tstamp)
        self.assertEqual(mok_track.call_count, 1)
        complete_args_dict = mok_track.call_args_list[0][1]
        self.assertEqual(len(complete_args_dict), 1)

        # payload
        actualUePr = json.loads(actual_pairs["ue_pr"])

        expectedUePr = {
            "data": {"data": {"n": "v"}, "schema": "test.schema"},
            "schema": UNSTRUCT_SCHEMA,
        }

        self.assertDictEqual(actualUePr, expectedUePr)
        self.assertEqual(actual_pairs["e"], "ue")

    @mock.patch("snowplow_tracker.Tracker.track")
    def test_track_self_describing_event_encode(self, mok_track: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track.side_effect = mocked_track

        t = Tracker("namespace", e, encode_base64=True)
        event_json = SelfDescribingJson("test.sde.schema", {"n": "v"})

        event = SelfDescribing(event_json=event_json)
        actual_pairs = event.build_payload(
            encode_base64=t.encode_base64,
            json_encoder=t.json_encoder,
        ).nv_pairs

        t.track_self_describing_event(event_json)
        self.assertEqual(mok_track.call_count, 1)
        complete_args_dict = mok_track.call_args_list[0][1]
        self.assertEqual(len(complete_args_dict), 1)
        self.assertTrue("ue_px" in actual_pairs.keys())

    @mock.patch("snowplow_tracker.Tracker.track")
    def test_track_struct_event(self, mok_track: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track.side_effect = mocked_track

        t = Tracker("namespace", e)
        ctx = SelfDescribingJson("test.context.schema", {"user": "tester"})
        ev_tstamp = 1399021242030
        t.track_struct_event(
            "Mixes",
            "Play",
            "Test",
            "TestProp",
            value=3.14,
            context=[ctx],
            tstamp=ev_tstamp,
        )
        self.assertEqual(mok_track.call_count, 1)
        complete_args_dict = mok_track.call_args_list[0][1]
        self.assertEqual(len(complete_args_dict), 1)

        actual_payload_arg = complete_args_dict["event"].payload
        actual_pairs = actual_payload_arg.nv_pairs

        expected_pairs = {
            "e": "se",
            "se_ca": "Mixes",
            "se_ac": "Play",
            "se_la": "Test",
            "se_pr": "TestProp",
            "se_va": 3.14,
        }
        self.assertDictEqual(actual_pairs, expected_pairs)

    @mock.patch("snowplow_tracker.Tracker.track")
    def test_track_page_view(self, mok_track: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track.side_effect = mocked_track

        t = Tracker("namespace", e)
        ctx = SelfDescribingJson("test.context.schema", {"user": "tester"})
        ev_tstamp = 1399021242030
        t.track_page_view(
            "example.com",
            "Example",
            "docs.snowplow.io",
            context=[ctx],
            tstamp=ev_tstamp,
        )
        self.assertEqual(mok_track.call_count, 1)
        complete_args_dict = mok_track.call_args_list[0][1]
        self.assertEqual(len(complete_args_dict), 1)

        actual_payload_arg = complete_args_dict["event"].payload
        actualPairs = actual_payload_arg.nv_pairs

        expectedPairs = {
            "e": "pv",
            "url": "example.com",
            "page": "Example",
            "refr": "docs.snowplow.io",
        }
        self.assertDictEqual(actualPairs, expectedPairs)

    @mock.patch("snowplow_tracker.Tracker.track")
    def test_track_page_ping(self, mok_track: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track.side_effect = mocked_track

        t = Tracker("namespace", e)
        ctx = SelfDescribingJson("test.context.schema", {"user": "tester"})
        ev_tstamp = 1399021242030
        t.track_page_ping(
            "example.com",
            "Example",
            "docs.snowplow.io",
            0,
            1,
            2,
            3,
            context=[ctx],
            tstamp=ev_tstamp,
        )
        self.assertEqual(mok_track.call_count, 1)
        complete_args_dict = mok_track.call_args_list[0][1]
        self.assertEqual(len(complete_args_dict), 1)

        actual_payload_arg = complete_args_dict["event"].payload
        actual_pairs = actual_payload_arg.nv_pairs

        expectedPairs = {
            "e": "pp",
            "url": "example.com",
            "page": "Example",
            "refr": "docs.snowplow.io",
            "pp_mix": 0,
            "pp_max": 1,
            "pp_miy": 2,
            "pp_may": 3,
        }
        self.assertDictEqual(actual_pairs, expectedPairs)

    @mock.patch("snowplow_tracker.Tracker.track")
    def test_track_ecommerce_transaction_item(self, mok_track: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track.side_effect = mocked_track

        t = Tracker("namespace", e)
        ctx = SelfDescribingJson("test.context.schema", {"user": "tester"})
        ev_tstamp = 1399021242030
        t.track_ecommerce_transaction_item(
            order_id="1234",
            sku="sku1234",
            price=3.14,
            quantity=1,
            name="itemName",
            category="itemCategory",
            currency="itemCurrency",
            context=[ctx],
            tstamp=ev_tstamp,
        )
        self.assertEqual(mok_track.call_count, 1)
        complete_args_list = mok_track.call_args_list[0][1]
        self.assertEqual(len(complete_args_list), 1)

        actual_payload_arg = complete_args_list["event"].payload
        actual_pairs = actual_payload_arg.nv_pairs

        expectedPairs = {
            "e": "ti",
            "ti_id": "1234",
            "ti_sk": "sku1234",
            "ti_nm": "itemName",
            "ti_ca": "itemCategory",
            "ti_pr": 3.14,
            "ti_qu": 1,
            "ti_cu": "itemCurrency",
        }
        self.assertDictEqual(actual_pairs, expectedPairs)

    @mock.patch("snowplow_tracker.Tracker.track")
    def test_track_ecommerce_transaction_no_items(self, mok_track: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track.side_effect = mocked_track

        t = Tracker("namespace", e)
        ctx = SelfDescribingJson("test.context.schema", {"user": "tester"})
        evTstamp = 1399021242030
        t.track_ecommerce_transaction(
            "1234",
            10,
            "transAffiliation",
            2.5,
            1.5,
            "transCity",
            "transState",
            "transCountry",
            "transCurrency",
            context=[ctx],
            tstamp=evTstamp,
        )
        self.assertEqual(mok_track.call_count, 1)
        completeArgsList = mok_track.call_args_list[0][1]
        self.assertEqual(len(completeArgsList), 1)

        actualPayloadArg = completeArgsList["event"].payload
        actualPairs = actualPayloadArg.nv_pairs

        expectedPairs = {
            "e": "tr",
            "tr_id": "1234",
            "tr_tt": 10,
            "tr_af": "transAffiliation",
            "tr_tx": 2.5,
            "tr_sh": 1.5,
            "tr_ci": "transCity",
            "tr_st": "transState",
            "tr_co": "transCountry",
            "tr_cu": "transCurrency",
        }
        self.assertDictEqual(actualPairs, expectedPairs)

    @mock.patch("snowplow_tracker.Tracker.track_ecommerce_transaction_item")
    @mock.patch("snowplow_tracker.Tracker.track")
    def test_track_ecommerce_transaction_with_items(
        self, mok_track: Any, mok_track_trans_item: Any
    ) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track.side_effect = mocked_track
        mok_track_trans_item.side_effect = mocked_track_trans_item

        t = Tracker("namespace", e)
        ctx = SelfDescribingJson("test.context.schema", {"user": "tester"})
        evTstamp = 1399021242030
        transItems = [
            {"sku": "sku1234", "quantity": 3, "price": 3.14},
            {"sku": "sku5678", "quantity": 1, "price": 2.72},
        ]
        t.track_ecommerce_transaction(
            order_id="1234",
            total_value=10,
            affiliation="transAffiliation",
            tax_value=2.5,
            shipping=1.5,
            city="transCity",
            state="transState",
            country="transCountry",
            currency="transCurrency",
            items=transItems,
            context=[ctx],
            tstamp=evTstamp,
        )

        # Transaction
        callCompleteArgsList = mok_track.call_args_list
        firstCallArgsList = callCompleteArgsList[0][1]
        self.assertEqual(len(firstCallArgsList), 1)

        actualPayloadArg = firstCallArgsList["event"].payload
        actualPairs = actualPayloadArg.nv_pairs

        expectedTransPairs = {
            "e": "tr",
            "tr_id": "1234",
            "tr_tt": 10,
            "tr_af": "transAffiliation",
            "tr_tx": 2.5,
            "tr_sh": 1.5,
            "tr_ci": "transCity",
            "tr_st": "transState",
            "tr_co": "transCountry",
            "tr_cu": "transCurrency",
        }
        self.assertDictEqual(actualPairs, expectedTransPairs)

        # Items
        calls_to_track_trans_item = mok_track_trans_item.call_count
        self.assertEqual(calls_to_track_trans_item, 2)
        callTrackItemsArgsList = mok_track_trans_item.call_args_list
        # 1st item
        firstItemCallArgs = callTrackItemsArgsList[0][0]
        self.assertEqual((), firstItemCallArgs)
        firstItemCallKwargs = callTrackItemsArgsList[0][1]

        expectedFirstItemPairs = {
            "sku": "sku1234",
            "quantity": 3,
            "price": 3.14,
            "order_id": "1234",
            "currency": "transCurrency",
            "tstamp": evTstamp,
            "event_subject": None,
            "context": [ctx],
        }

        self.assertDictEqual(firstItemCallKwargs, expectedFirstItemPairs)
        # 2nd item
        secItemCallArgs = callTrackItemsArgsList[1][0]
        self.assertEqual((), secItemCallArgs)
        secItemCallKwargs = callTrackItemsArgsList[1][1]

        expectedSecItemPairs = {
            "sku": "sku5678",
            "quantity": 1,
            "price": 2.72,
            "order_id": "1234",
            "currency": "transCurrency",
            "tstamp": evTstamp,
            "event_subject": None,
            "context": [ctx],
        }

        self.assertDictEqual(secItemCallKwargs, expectedSecItemPairs)

    @mock.patch("snowplow_tracker.Tracker.track_self_describing_event")
    def test_track_link_click(self, mok_track_unstruct: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track_unstruct.side_effect = mocked_track_unstruct

        t = Tracker("namespace", e)
        ctx = SelfDescribingJson("test.context.schema", {"user": "tester"})
        evTstamp = 1399021242030

        t.track_link_click(
            "example.com",
            "elemId",
            ["elemClass1", "elemClass2"],
            "_blank",
            "elemContent",
            context=[ctx],
            tstamp=evTstamp,
        )

        expected = {
            "schema": LINK_CLICK_SCHEMA,
            "data": {
                "targetUrl": "example.com",
                "elementId": "elemId",
                "elementClasses": ["elemClass1", "elemClass2"],
                "elementTarget": "_blank",
                "elementContent": "elemContent",
            },
        }

        callArgs = mok_track_unstruct.call_args_list[0][1]
        self.assertEqual(len(callArgs), 4)
        self.assertDictEqual(callArgs["event_json"].to_json(), expected)
        self.assertIs(callArgs["context"][0], ctx)
        self.assertEqual(callArgs["tstamp"], evTstamp)

    @mock.patch("snowplow_tracker.Tracker.track_self_describing_event")
    def test_track_link_click_optional_none(self, mok_track_unstruct: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track_unstruct.side_effect = mocked_track_unstruct

        t = Tracker("namespace", e)

        t.track_link_click("example.com")

        expected = {
            "schema": LINK_CLICK_SCHEMA,
            "data": {
                "targetUrl": "example.com",
            },
        }

        callArgs = mok_track_unstruct.call_args_list[0][1]
        self.assertEqual(len(callArgs), 4)
        self.assertDictEqual(callArgs["event_json"].to_json(), expected)
        self.assertTrue(callArgs["context"] is None)
        self.assertTrue(callArgs["tstamp"] is None)

    @mock.patch("snowplow_tracker.Tracker.track_self_describing_event")
    def test_track_add_to_cart(self, mok_track_unstruct: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track_unstruct.side_effect = mocked_track_unstruct

        t = Tracker("namespace", e)
        ctx = SelfDescribingJson("test.context.schema", {"user": "tester"})
        evTstamp = 1399021242030

        t.track_add_to_cart(
            "sku1234",
            3,
            "testName",
            "testCategory",
            3.14,
            "testCurrency",
            context=[ctx],
            tstamp=evTstamp,
        )

        expected = {
            "schema": ADD_TO_CART_SCHEMA,
            "data": {
                "sku": "sku1234",
                "quantity": 3,
                "name": "testName",
                "category": "testCategory",
                "unitPrice": 3.14,
                "currency": "testCurrency",
            },
        }

        callArgs = mok_track_unstruct.call_args_list[0][1]
        self.assertEqual(len(callArgs), 4)
        self.assertDictEqual(callArgs["event_json"].to_json(), expected)
        self.assertIs(callArgs["context"][0], ctx)
        self.assertEqual(callArgs["tstamp"], evTstamp)

    @mock.patch("snowplow_tracker.Tracker.track_self_describing_event")
    def test_track_add_to_cart_optional_none(self, mok_track_unstruct: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track_unstruct.side_effect = mocked_track_unstruct

        t = Tracker("namespace", e)

        t.track_add_to_cart("sku1234", 1)

        expected = {
            "schema": ADD_TO_CART_SCHEMA,
            "data": {"sku": "sku1234", "quantity": 1},
        }

        callArgs = mok_track_unstruct.call_args_list[0][1]
        self.assertEqual(len(callArgs), 4)
        self.assertDictEqual(callArgs["event_json"].to_json(), expected)
        self.assertTrue(callArgs["context"] is None)
        self.assertTrue(callArgs["tstamp"] is None)

    @mock.patch("snowplow_tracker.Tracker.track_self_describing_event")
    def test_track_remove_from_cart(self, mok_track_unstruct: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track_unstruct.side_effect = mocked_track_unstruct

        t = Tracker("namespace", e)
        ctx = SelfDescribingJson("test.context.schema", {"user": "tester"})
        evTstamp = 1399021242030

        t.track_remove_from_cart(
            "sku1234",
            3,
            "testName",
            "testCategory",
            3.14,
            "testCurrency",
            context=[ctx],
            tstamp=evTstamp,
        )

        expected = {
            "schema": REMOVE_FROM_CART_SCHEMA,
            "data": {
                "sku": "sku1234",
                "quantity": 3,
                "name": "testName",
                "category": "testCategory",
                "unitPrice": 3.14,
                "currency": "testCurrency",
            },
        }

        callArgs = mok_track_unstruct.call_args_list[0][1]
        self.assertEqual(len(callArgs), 4)
        self.assertDictEqual(callArgs["event_json"].to_json(), expected)
        self.assertIs(callArgs["context"][0], ctx)
        self.assertEqual(callArgs["tstamp"], evTstamp)

    @mock.patch("snowplow_tracker.Tracker.track_self_describing_event")
    def test_track_remove_from_cart_optional_none(
        self, mok_track_unstruct: Any
    ) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track_unstruct.side_effect = mocked_track_unstruct

        t = Tracker("namespace", e)

        t.track_remove_from_cart("sku1234", 1)

        expected = {
            "schema": REMOVE_FROM_CART_SCHEMA,
            "data": {"sku": "sku1234", "quantity": 1},
        }

        callArgs = mok_track_unstruct.call_args_list[0][1]
        self.assertEqual(len(callArgs), 4)
        self.assertDictEqual(callArgs["event_json"].to_json(), expected)
        self.assertTrue(callArgs["context"] is None)
        self.assertTrue(callArgs["tstamp"] is None)

    @mock.patch("snowplow_tracker.Tracker.track_self_describing_event")
    def test_track_form_change(self, mok_track_unstruct: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track_unstruct.side_effect = mocked_track_unstruct

        t = Tracker("namespace", e)
        ctx = SelfDescribingJson("test.context.schema", {"user": "tester"})
        evTstamp = 1399021242030

        t.track_form_change(
            "testFormId",
            "testElemId",
            "INPUT",
            "testValue",
            "text",
            ["testClass1", "testClass2"],
            context=[ctx],
            tstamp=evTstamp,
        )

        expected = {
            "schema": FORM_CHANGE_SCHEMA,
            "data": {
                "formId": "testFormId",
                "elementId": "testElemId",
                "nodeName": "INPUT",
                "value": "testValue",
                "type": "text",
                "elementClasses": ["testClass1", "testClass2"],
            },
        }

        callArgs = mok_track_unstruct.call_args_list[0][1]
        self.assertEqual(len(callArgs), 4)
        self.assertDictEqual(callArgs["event_json"].to_json(), expected)
        self.assertIs(callArgs["context"][0], ctx)
        self.assertEqual(callArgs["tstamp"], evTstamp)

    @mock.patch("snowplow_tracker.Tracker.track_self_describing_event")
    def test_track_form_change_optional_none(self, mok_track_unstruct: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track_unstruct.side_effect = mocked_track_unstruct

        t = Tracker("namespace", e)
        t.track_form_change("testFormId", "testElemId", "INPUT", "testValue")

        expected = {
            "schema": FORM_CHANGE_SCHEMA,
            "data": {
                "formId": "testFormId",
                "elementId": "testElemId",
                "nodeName": "INPUT",
                "value": "testValue",
            },
        }

        callArgs = mok_track_unstruct.call_args_list[0][1]
        self.assertEqual(len(callArgs), 4)
        self.assertDictEqual(callArgs["event_json"].to_json(), expected)
        self.assertTrue(callArgs["context"] is None)
        self.assertTrue(callArgs["tstamp"] is None)

    @mock.patch("snowplow_tracker.Tracker.track_self_describing_event")
    def test_track_form_submit(self, mok_track_unstruct: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track_unstruct.side_effect = mocked_track_unstruct

        t = Tracker("namespace", e)
        ctx = SelfDescribingJson("test.context.schema", {"user": "tester"})
        evTstamp = 1399021242030
        elems = [
            {
                "name": "user_email",
                "value": "fake@email.fake",
                "nodeName": "INPUT",
                "type": "email",
            }
        ]

        t.track_form_submit(
            "testFormId",
            ["testClass1", "testClass2"],
            elems,
            context=[ctx],
            tstamp=evTstamp,
        )

        expected = {
            "schema": FORM_SUBMIT_SCHEMA,
            "data": {
                "formId": "testFormId",
                "formClasses": ["testClass1", "testClass2"],
                "elements": elems,
            },
        }

        callArgs = mok_track_unstruct.call_args_list[0][1]
        self.assertEqual(len(callArgs), 4)
        self.assertDictEqual(callArgs["event_json"].to_json(), expected)
        self.assertIs(callArgs["context"][0], ctx)
        self.assertEqual(callArgs["tstamp"], evTstamp)

    @mock.patch("snowplow_tracker.Tracker.track_self_describing_event")
    def test_track_form_submit_invalid_element_type(
        self, mok_track_unstruct: Any
    ) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track_unstruct.side_effect = mocked_track_unstruct

        t = Tracker("namespace", e)
        ctx = SelfDescribingJson("test.context.schema", {"user": "tester"})
        evTstamp = 1399021242030
        elems = [
            {
                "name": "user_email",
                "value": "fake@email.fake",
                "nodeName": "INPUT",
                "type": "invalid",
            }
        ]

        with self.assertRaises(ValueError):
            t.track_form_submit(
                "testFormId",
                ["testClass1", "testClass2"],
                elems,
                context=[ctx],
                tstamp=evTstamp,
            )

    @mock.patch("snowplow_tracker.Tracker.track_self_describing_event")
    def test_track_form_submit_invalid_element_type_disabled_contracts(
        self, mok_track_unstruct: Any
    ) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track_unstruct.side_effect = mocked_track_unstruct

        t = Tracker("namespace", e)
        ctx = SelfDescribingJson("test.context.schema", {"user": "tester"})
        evTstamp = 1399021242030
        elems = [
            {
                "name": "user_email",
                "value": "fake@email.fake",
                "nodeName": "INPUT",
                "type": "invalid",
            }
        ]

        with ContractsDisabled():
            t.track_form_submit(
                "testFormId",
                ["testClass1", "testClass2"],
                elems,
                context=[ctx],
                tstamp=evTstamp,
            )

        expected = {
            "schema": FORM_SUBMIT_SCHEMA,
            "data": {
                "formId": "testFormId",
                "formClasses": ["testClass1", "testClass2"],
                "elements": elems,
            },
        }

        callArgs = mok_track_unstruct.call_args_list[0][1]
        self.assertEqual(len(callArgs), 4)
        self.assertDictEqual(callArgs["event_json"].to_json(), expected)
        self.assertIs(callArgs["context"][0], ctx)
        self.assertEqual(callArgs["tstamp"], evTstamp)

    @mock.patch("snowplow_tracker.Tracker.track_self_describing_event")
    def test_track_form_submit_optional_none(self, mok_track_unstruct: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track_unstruct.side_effect = mocked_track_unstruct

        t = Tracker("namespace", e)
        t.track_form_submit("testFormId")

        expected = {"schema": FORM_SUBMIT_SCHEMA, "data": {"formId": "testFormId"}}

        callArgs = mok_track_unstruct.call_args_list[0][1]
        self.assertEqual(len(callArgs), 4)
        self.assertDictEqual(callArgs["event_json"].to_json(), expected)
        self.assertTrue(callArgs["context"] is None)
        self.assertTrue(callArgs["tstamp"] is None)

    @mock.patch("snowplow_tracker.Tracker.track_self_describing_event")
    def test_track_form_submit_empty_elems(self, mok_track_unstruct: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track_unstruct.side_effect = mocked_track_unstruct

        t = Tracker("namespace", e)
        t.track_form_submit("testFormId", elements=[])

        expected = {"schema": FORM_SUBMIT_SCHEMA, "data": {"formId": "testFormId"}}

        callArgs = mok_track_unstruct.call_args_list[0][1]
        self.assertEqual(len(callArgs), 4)
        self.assertDictEqual(callArgs["event_json"].to_json(), expected)

    @mock.patch("snowplow_tracker.Tracker.track_self_describing_event")
    def test_track_site_search(self, mok_track_unstruct: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track_unstruct.side_effect = mocked_track_unstruct

        t = Tracker("namespace", e)
        ctx = SelfDescribingJson("test.context.schema", {"user": "tester"})
        evTstamp = 1399021242030

        t.track_site_search(
            ["track", "search"], {"new": True}, 100, 10, context=[ctx], tstamp=evTstamp
        )

        expected = {
            "schema": SITE_SEARCH_SCHEMA,
            "data": {
                "terms": ["track", "search"],
                "filters": {"new": True},
                "totalResults": 100,
                "pageResults": 10,
            },
        }

        callArgs = mok_track_unstruct.call_args_list[0][1]

        self.assertEqual(len(callArgs), 4)
        self.assertDictEqual(callArgs["event_json"].to_json(), expected)
        self.assertIs(callArgs["context"][0], ctx)
        self.assertEqual(callArgs["tstamp"], evTstamp)

    @mock.patch("snowplow_tracker.Tracker.track_self_describing_event")
    def test_track_site_search_optional_none(self, mok_track_unstruct: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track_unstruct.side_effect = mocked_track_unstruct

        t = Tracker("namespace", e)
        t.track_site_search(["track", "search"])

        expected = {
            "schema": SITE_SEARCH_SCHEMA,
            "data": {"terms": ["track", "search"]},
        }

        callArgs = mok_track_unstruct.call_args_list[0][1]
        self.assertEqual(len(callArgs), 4)
        self.assertDictEqual(callArgs["event_json"].to_json(), expected)
        self.assertTrue(callArgs["context"] is None)
        self.assertTrue(callArgs["tstamp"] is None)

    @mock.patch("snowplow_tracker.Tracker.track")
    def test_track_mobile_screen_view(self, mok_track: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track.side_effect = mocked_track

        t = Tracker("namespace", e)

        screen_view = ScreenView(name="screenName", id_="screenId")
        actual_pairs = screen_view.build_payload(
            encode_base64=False,
            json_encoder=t.json_encoder,
        ).nv_pairs

        t.track(screen_view)

        self.assertEqual(mok_track.call_count, 1)
        complete_args_dict = mok_track.call_args_list[0][0]
        self.assertEqual(len(complete_args_dict), 1)
        actual_ue_pr = json.loads(actual_pairs["ue_pr"])

        expected = {
            "schema": MOBILE_SCREEN_VIEW_SCHEMA,
            "data": {"id": "screenId", "name": "screenName"},
        }

        complete_args_dict = mok_track.call_args_list[0][1]
        complete_args_dict = mok_track.call_args_list[0][1]
        self.assertDictEqual(actual_ue_pr["data"], expected)

    @mock.patch("snowplow_tracker.Tracker.track_self_describing_event")
    def test_track_screen_view(self, mok_track_unstruct: Any) -> None:
        mokEmitter = self.create_patch("snowplow_tracker.Emitter")
        e = mokEmitter()

        mok_track_unstruct.side_effect = mocked_track_unstruct

        t = Tracker("namespace", e)
        ctx = SelfDescribingJson("test.context.schema", {"user": "tester"})
        evTstamp = 1399021242030

        t.track_screen_view("screenName", "screenId", context=[ctx], tstamp=evTstamp)

        expected = {
            "schema": SCREEN_VIEW_SCHEMA,
            "data": {"name": "screenName", "id": "screenId"},
        }

        callArgs = mok_track_unstruct.call_args_list[0][1]
        self.assertEqual(len(callArgs), 4)
        self.assertDictEqual(callArgs["event_json"].to_json(), expected)
        self.assertIs(callArgs["context"][0], ctx)
        self.assertEqual(callArgs["tstamp"], evTstamp)
