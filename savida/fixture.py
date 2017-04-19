import contextlib
import multiprocessing

from savida.server import Server


class ServerWrapper(object):

    def __init__(self, server):
        self._proc = None
        self.server = server

    def start(self):
        self._proc = multiprocessing.Process(target=self.server.start)
        self._proc.start()
        return self

    def stop(self):
        if self._proc is not None:
            self._proc.terminate()
            self._proc.join()
        self._proc = None

    @property
    def base_url(self):
        if self._proc is None:
            raise RuntimeError("Server was not started yet, no base_url set")
        return self.server.base_url


@contextlib.contextmanager
def http_server(*args, **kwargs):
    server = ServerWrapper(Server(*args, **kwargs))
    try:
        yield server
    finally:
        server.stop()
