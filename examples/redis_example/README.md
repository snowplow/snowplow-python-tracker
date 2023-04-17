# Redis Example App

This example shows how to set up the Python tracker with a Redis database and a Redis worker to forward events to a Snowplow pipeline.

#### Installation
- Install the Python tracker from the root folder of the project.

`python setup.py install` 

- Install redis for your machine. More information can be found [here](https://redis.io/docs/getting-started/installation/)

`brew install redis`

- Run `redis-server` to check your redis installation, to stop the server enter `ctrl+c`.

#### Usage
Navigate to the example folder.

`cd examples/redis_example`

This example has two programmes, `redis_app.py` tracks events and sends them to a redis database, `redis_worker.py` then forwards these events onto a Snowplow pipeline.

To send events to your pipeline, run `redis-server`, followed by the `redis_worker.py {{your_collector_endpoint}}` and finally `redis_app.py`. You should see 3 events in your pipleine.



