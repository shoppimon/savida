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

    def __getattr__(self, item):
        return getattr(self.server, item)


@contextlib.contextmanager
def http_server(*args, **kwargs):
    server = ServerWrapper(Server(*args, **kwargs))
    try:
        yield server
    finally:
        server.stop()
