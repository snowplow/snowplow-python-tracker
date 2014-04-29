import requests
import json

DEFAULT_MAX_LENGTH = 10
HTTP_ERRORS = {"host not found",
               "No address associated with name",
               "No address associated with hostname"}

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

class BufferedConsumer(object):

    def __init__(self, endpoint, max_length=DEFAULT_MAX_LENGTH):

        self.endpoint = endpoint
        self.max_length = max_length
        self.queue = []

    def input(self, payload):

        print(len(self.queue))
        self.queue.append(payload.context)
        if len(self.queue) >= self.max_length:
            self.flush()

    def flush(self):
        
        batch = json.dumps(self.queue)
        self.queue = []
        r = requests.post(self.endpoint, data=batch);
