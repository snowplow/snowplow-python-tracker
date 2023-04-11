This example shows how to set up the Python tracker with a Redis database and a Redis worker to forward events to a Snowplow pipeline.

#### Installation
- Install redis for your machine. More information can be found [here](https://redis.io/docs/getting-started/installation/)

`brew install redis`

- Run `redis-server` to check your redis installation, to stop the server enter `ctrl+c`.

#### Usage
This example has two programmes, `redis_app.py` tracks events and sends them to a redis database, `redis_worker.py` then forwards these events onto a Snowplow pipeline.

To send events to your pipeline, run `redis-server`, followed by the `redis_worker.py` and finally `redis_app.py {{your_collector_endpoint}}`. You should see 3 events in your pipleine.



