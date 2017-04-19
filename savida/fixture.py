import contextlib
import multiprocessing

from .server import Server


class ServerWrapper(object):

    def __init__(self, server):
        self._proc = None
        self.server = server

<<<<<<< HEAD
    @property
    def base_url(self):
        return self.server.base_url

    def start(self):
=======
    def serve(self):
>>>>>>> 1575672fd73b561cc727112128d332daafce5580
        self._proc = multiprocessing.Process(target=self.server.start)
        self._proc.start()
        return self

    def stop(self):
<<<<<<< HEAD
        if self._proc is not None:
            self._proc.terminate()
            self._proc.join()
        self._proc = None
=======
        self._proc.terminate()
        self._proc.join()

    @property
    def base_url(self):
        if self._proc is None:
            raise RuntimeError("Server was not started yet, no base_url set")
        return self.server.base_url

>>>>>>> 1575672fd73b561cc727112128d332daafce5580

@contextlib.contextmanager
def http_server(*args, **kwargs):
    server = ServerWrapper(Server(*args, **kwargs))
    try:
        yield server
    finally:
        server.stop()
