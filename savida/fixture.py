import contextlib
import multiprocessing

from .server import Server


class ServerWrapper(object):

    def __init__(self, server):
        self._proc = None
        self.server = server

    def start(self):
        self._proc = multiprocessing.Process(target=self.server.start)
        self._proc.start()
        return self

    def stop(self):
        self._proc.terminate()
        self._proc.join()


@contextlib.contextmanager
def http_server(*args, **kwargs):
    server = ServerWrapper(Server(*args, **kwargs))
    try:
        yield server
    finally:
        server.stop()
