from distutils.log import error
from snowplow_tracker import (
    Tracker,
    Emitter,
    Subject,
    SelfDescribingJson,
    PageView,
    PagePing,
    SelfDescribing,
    ScreenView,
    StructuredEvent,
)
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

    t = Tracker(namespace="snowplow_tracker", emitters=e, subject=s)

    print("Sending events to " + e.endpoint)

    page_view = PageView(
        page_url="https://www.snowplow.io",
        page_title="Homepage",
        event_subject=t.subject,
    )
    t.track(page_view)

    page_ping = PagePing(
        page_url="https://www.snowplow.io",
        page_title="Homepage",
        event_subject=t.subject,
    )
    t.track(page_ping)

    link_click = SelfDescribing(
        SelfDescribingJson(
            "iglu:com.snowplowanalytics.snowplow/link_click/jsonschema/1-0-1",
            {"targetUrl": "https://www.snowplow.io"},
        ),
        event_subject=t.subject,
    )
    t.track(link_click)

    screen_view = ScreenView(id_="id", name="name", event_subject=t.subject)
    t.track(screen_view)

    struct_event = StructuredEvent(
        category="shop",
        action="add-to-basket",
        property_="pcs",
        value=2,
        event_subject=t.subject,
    )
    t.track(struct_event)
    t.flush()


if __name__ == "__main__":
    main()
