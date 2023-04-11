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

