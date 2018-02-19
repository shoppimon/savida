"""Savida HTTP testing server - test fixture wrapper
"""

# Copyright (c) 2017 Shoppimon LTD
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import contextlib
import multiprocessing
import socket
import time

from savida.server import Server


class ServerWrapper(object):

    UP_CHECK_INTERVAL = 0.01
    UP_TIMEOUT = 10

    def __init__(self, server):
        self._proc = None
        self.server = server

    def start(self):
        self._proc = multiprocessing.Process(target=self.server.start)
        self._proc.start()
        self._wait_for_server_up()
        return self

    def stop(self):
        if self._proc is not None:
            self._proc.terminate()
            self._proc.join()

    def _wait_for_server_up(self):
        for _ in range(int(self.UP_TIMEOUT / self.UP_CHECK_INTERVAL)):
            s = socket.socket()
            try:
                s.connect((self.server.host, self.server.port))
                return True
            except socket.error as e:
                time.sleep(self.UP_CHECK_INTERVAL)
        raise RuntimeError("Could not verify that server is up after %d seconds", self.UP_TIMEOUT)

    def __getattr__(self, item):
        return getattr(self.server, item)


@contextlib.contextmanager
def http_server(*args, **kwargs):
    server = ServerWrapper(Server(*args, **kwargs))
    try:
        yield server
    finally:
        server.stop()
