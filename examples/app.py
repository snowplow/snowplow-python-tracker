from distutils.log import error
from snowplow_tracker import Tracker, Emitter, Subject
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


if __name__ == '__main__':
    main()
