import sys
from snowplow_tracker import (
    Snowplow,
    EmitterConfiguration,
    Subject,
    TrackerConfiguration,
    SelfDescribingJson,
)


def get_url_from_args():
    if len(sys.argv) != 2:
        raise ValueError("Collector Endpoint is required")
    return sys.argv[1]


def main():

    collector_url = get_url_from_args()
    # Configure Emitter
    emitter_config = EmitterConfiguration(buffer_size=5)

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

    tracker.track_page_view("https://www.snowplow.io", "Homepage")
    tracker.track_page_ping("https://www.snowplow.io", "Homepage")
    tracker.track_link_click("https://www.snowplow.io/about")
    tracker.track_page_view("https://www.snowplow.io/about", "About")

    tracker.track_self_describing_event(
        SelfDescribingJson(
            "iglu:com.snowplowanalytics.snowplow/link_click/jsonschema/1-0-1",
            {"targetUrl": "example.com"},
        )
    )
    tracker.track_struct_event("shop", "add-to-basket", None, "pcs", 2)

    tracker.flush()


if __name__ == "__main__":
    main()
