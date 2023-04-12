import sys
from snowplow_tracker import Emitter
from typing import Any
from snowplow_tracker.typing import PayloadDict
import json
import redis
import signal
import gevent
from gevent.pool import Pool


def get_url_from_args():
    if len(sys.argv) != 2:
        raise ValueError("Collector Endpoint is required")
    return sys.argv[1]


class RedisWorker:
    def __init__(self, emitter: Emitter, key) -> None:
        self.pool = Pool(5)
        self.emitter = emitter
        self.rdb = redis.StrictRedis()
        self.key = key

        signal.signal(signal.SIGTERM, self.request_shutdown)
        signal.signal(signal.SIGINT, self.request_shutdown)
        signal.signal(signal.SIGQUIT, self.request_shutdown)

    def send(self, payload: PayloadDict) -> None:
        """
        Send an event to an emitter
        """
        self.emitter.input(payload)

    def pop_payload(self) -> None:
        """
        Get a single event from Redis and send it
        If the Redis queue is empty, sleep to avoid making continual requests
        """
        payload = self.rdb.lpop(self.key)
        if payload:
            self.pool.spawn(self.send, json.loads(payload.decode("utf-8")))
        else:
            gevent.sleep(5)

    def run(self) -> None:
        """
        Run indefinitely
        """
        self._shutdown = False
        while not self._shutdown:
            self.pop_payload()
        self.pool.join(timeout=20)

    def request_shutdown(self, *args: Any) -> None:
        """
        Halt the worker
        """
        self._shutdown = True


def main():
    collector_url = get_url_from_args()

    # Configure Emitter
    emitter = Emitter(collector_url, batch_size=1)

    # Setup worker
    worker = RedisWorker(emitter=emitter, key="redis_key")
    worker.run()


if __name__ == "__main__":
    main()
