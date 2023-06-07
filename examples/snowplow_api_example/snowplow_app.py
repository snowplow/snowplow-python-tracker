import sys
from snowplow_tracker import (
    Snowplow,
    EmitterConfiguration,
    Subject,
    TrackerConfiguration,
    SelfDescribingJson,
    PagePing,
    PageView,
    ScreenView,
    SelfDescribing,
    StructuredEvent,
)


def get_url_from_args():
    if len(sys.argv) != 2:
        raise ValueError("Collector Endpoint is required")
    return sys.argv[1]


def main():
    collector_url = get_url_from_args()
    # Configure Emitter
    custom_retry_codes = {500: False, 401: True}
    emitter_config = EmitterConfiguration(
        batch_size=5, custom_retry_codes=custom_retry_codes
    )

    # Configure Tracker
    tracker_config = TrackerConfiguration(encode_base64=True)

    # Initialise subject
    subject = Subject()
    subject.set_user_id("uid")

    Snowplow.create_tracker(
        namespace="ns",
        endpoint=collector_url,
        app_id="app1",
        subject=subject,
        tracker_config=tracker_config,
        emitter_config=emitter_config,
    )

    tracker = Snowplow.get_tracker("ns")

    page_view = PageView(page_url="https://www.snowplow.io", page_title="Homepage")
    tracker.track(page_view)

    page_ping = PagePing(page_url="https://www.snowplow.io", page_title="Homepage")
    tracker.track(page_ping)

    link_click = SelfDescribing(
        SelfDescribingJson(
            "iglu:com.snowplowanalytics.snowplow/link_click/jsonschema/1-0-1",
            {"targetUrl": "https://www.snowplow.io"},
        )
    )
    tracker.track(link_click)

    screen_view = ScreenView(id_="id", name="name")
    tracker.track(screen_view)

    struct_event = StructuredEvent(
        category="shop", action="add-to-basket", property_="pcs", value=2
    )
    tracker.track(struct_event)
    tracker.flush()


if __name__ == "__main__":
    main()
