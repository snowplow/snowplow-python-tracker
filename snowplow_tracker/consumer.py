import requests
import json
import threading

DEFAULT_MAX_LENGTH = 10
HTTP_ERRORS = {"host not found",
               "No address associated with name",
               "No address associated with hostname"}

class SendThread(threading.Thread):
    def __init__(self, consumer, payload):
        super(SendThread, self).__init__()
        self.consumer = consumer
        self.payload = payload

    def run(self):
        self.consumer.input(self.payload, False)


class FlushThread(threading.Thread):
    def __init__(self, consumer):
        super(FlushThread, self).__init__()
        self.consumer = consumer

    def run(self):
        self.consumer.flush(False)


class Consumer(object):

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def input(self, payload):

        """
            Send a GET request to the collector URI (generated from the
            new_tracker methods) and return the relevant error message if any.

            :param  payload:        Generated dict track()
            :type   payload:        payload
            :rtype:                 tuple(bool, int | str)
        """

        r = requests.get(self.endpoint, params=payload.context)
        code = r.status_code
        if code in HTTP_ERRORS:
            return (False, "Host [" + r.url + "] not found (possible connectivity error)")
        elif code < 0 or code >= 400:
            return (False, code)
        else:
            return (True, code)


class AsyncConsumer(Consumer):

    def __init__(self, endpoint):
        super(AsyncConsumer, self).__init__(endpoint)

    def input(self, payload, async=True):

        if async:
            self.sending_thread = SendThread(self, payload)
            self.sending_thread.start()
        else:
            super(AsyncConsumer, self).input(payload)


class BufferedConsumer(object):

    def __init__(self, endpoint, max_length=DEFAULT_MAX_LENGTH):

        self.endpoint = endpoint
        self.max_length = max_length
        self.queue = []

    def input(self, payload):

        self.queue.append(payload.context)
        if len(self.queue) >= self.max_length:
            self.flush()

    def flush(self):
        
        batch = json.dumps(self.queue)
        self.queue = []
        r = requests.post(self.endpoint, data=batch);


class AsyncBufferedConsumer(BufferedConsumer):

    def __init(self, endpoint, max_length=DEFAULT_MAX_LENGTH):
        super(AsyncBufferedConsumer, self).__init__(endpoint, max_length)

    def flush(self, async=True):
        if async:
            self.flushing_thread = FlushThread(self)
            self.flushing_thread.start()            
        else:
            super(AsyncBufferedConsumer, self).flush()
