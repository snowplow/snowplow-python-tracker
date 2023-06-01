from snowplow_tracker import (
    Tracker,
    ScreenView,
    PagePing,
    PageView,
    SelfDescribing,
    StructEvent,
    SelfDescribingJson,
)
from snowplow_tracker.typing import PayloadDict
import json
import redis
import logging

# logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RedisEmitter(object):
    """
    Sends Snowplow events to a Redis database
    """

    def __init__(self, rdb=None, key: str = "redis_key") -> None:
        """
        :param rdb:  Optional custom Redis database
        :type  rdb:  redis | None
        :param key:  The Redis key for the list of events
        :type  key:  string
        """

        if rdb is None:
            rdb = redis.StrictRedis()

        self.rdb = rdb
        self.key = key

    def input(self, payload: PayloadDict) -> None:
        """
        :param payload:  The event properties
        :type  payload:  dict(string:*)
        """
        logger.info("Pushing event to Redis queue...")
        self.rdb.rpush(self.key, json.dumps(payload))
        logger.info("Finished sending event to Redis.")

    def flush(self) -> None:
        logger.warning("The RedisEmitter class does not need to be flushed")
        return

    def sync_flush(self) -> None:
        self.flush()


def main():
    emitter = RedisEmitter()

    t = Tracker(namespace="snowplow_tracker", emitters=emitter)

    page_view = PageView(page_url="https://www.snowplow.io", page_title="Homepage")
    t.track(page_view)

    page_ping = PagePing(page_url="https://www.snowplow.io", page_title="Homepage")
    t.track(page_ping)

    link_click = SelfDescribing(
        SelfDescribingJson(
            "iglu:com.snowplowanalytics.snowplow/link_click/jsonschema/1-0-1",
            {"targetUrl": "https://www.snowplow.io"},
        )
    )
    t.track(link_click)

    screen_view = ScreenView(id_="id", name="name")
    t.track(screen_view)

    struct_event = StructEvent(
        category="shop", action="add-to-basket", property_="pcs", value=2
    )
    t.track(struct_event)


if __name__ == "__main__":
    main()
