"""
    file_worker.py
"""

from pygtail import Pygtail
import json
import signal

class FileWorker(object):
    """
        Synchronously read events from file and send them to an emitter
    """

    def __init__(self, emitter, filename):
        self.emitter = emitter
        self.pygtail = Pygtail(filename, paranoid=True)

        signal.signal(signal.SIGTERM, self.request_shutdown)
        signal.signal(signal.SIGINT, self.request_shutdown)
        signal.signal(signal.SIGQUIT, self.request_shutdown)

    def send(self, payload):
        """
            Send an event to an emitter
        """
        self.emitter.input(payload)

    def run(self):
        """
            Run indefinitely
        """
        self._shutdown = False

        while not self._shutdown:
            payload = self.pygtail.next()
            self.send(json.loads(payload.decode("utf-8")))

    def request_shutdown(self, *args):
        """
            Halt the worker
        """
        self._shutdown = True
