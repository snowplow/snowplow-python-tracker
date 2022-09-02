from distutils.log import error
from snowplow_tracker import Tracker, Emitter, Subject, SelfDescribingJson
import sys


def get_url_from_args():
    if len(sys.argv) != 2:
        raise ValueError("Collector Endpoint is required")
    return sys.argv[1]


def main():
    collector_url = get_url_from_args()

    e = Emitter(collector_url)

    s = Subject().set_platform("pc")
    s.set_lang("en").set_user_id("test_user")

    t = Tracker(e, s)

    print("Sending events to " + collector_url)

    t.track_page_view("https://www.snowplowanalytics.com", "Homepage")
    t.track_page_ping("https://www.snowplowanalytics.com", "Homepage")
    t.track_link_click("https://www.snowplowanalytics.com")

    t.track_self_describing_event(
        SelfDescribingJson(
            "iglu:com.snowplowanalytics.snowplow/link_click/jsonschema/1-0-1",
            {"targetUrl": "example.com"},
        )
    )
    t.track_struct_event("shop", "add-to-basket", None, "pcs", 2)


if __name__ == "__main__":
    main()
