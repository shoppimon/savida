"""Savida testing HTTP server - main library
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

import socket
import time

from werkzeug.wrappers import Request
from werkzeug.wrappers import Response
from werkzeug.serving import run_simple
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.routing import Map
from werkzeug.routing import Rule
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import NotFound


class WSGIApplication(object):

    def __init__(self, app):
        self.url_map = Map([])
        self.app = app

    def __call__(self, environ, start_response):
        # try to match URL from url_map
        request = Request(environ)
        adapter = self.url_map.bind_to_environ(request)

        try:
            endpoint, values = adapter.match()
            response = endpoint(request, **values)
            return response(environ, start_response)
        except HTTPException:
            # if none of the urls matched, delegate to next middleware
            return self.app(environ, start_response)


class Server(object):

    def __init__(self, document_root=None):
        self._app = None
        self.rules = []
        self.document_root = document_root
        self.host = '127.0.0.1'
        self.port = _find_free_port()

    def when(self, path, methods=None):
        rule = RuleMaker(self, path, methods)
        return rule

    def start(self):
        middleware = NotFound()
        if self.document_root:
            # middleware for serving static files
            middleware = SharedDataMiddleware(middleware,
                                              {"/": self.document_root})

        self._app = WSGIApplication(middleware)

        # plug the rules
        self._app.url_map = Map(self.rules)

        run_simple(self.host, self.port, self._app, threaded=True)

    @property
    def base_url(self):
        if self.port is None:
            raise RuntimeError("Server was not started, base_url is unknown")
        return 'http://{}:{}'.format(self.host, self.port)


class RuleMaker(object):
    """An object responsible for creating routing rules
    """

    def __init__(self, server, path, methods=None):
        self.server = server
        self.path = path
        self.methods = methods

    def response(self, *args, **kwargs):
        """Return a response when the rule is invoked
        """
        def f(_):
            return Response(*args, **kwargs)
        self._make_rule(f)
        return self

    def call(self, callback):
        """Call a callback when the rule is invoked
        """
        self._make_rule(callback)
        return self

    def wait(self, delay):
        """Delay the response when the rule is matched
        """
        def f(_):
            time.sleep(delay)
            # Raise exception so that we proceed to the next middleware
            raise NotFound()
        self._make_rule(f)
        return self

    def _make_rule(self, callback):
        """Create and inject the rule into the server's list of rules
        """
        rule = Rule(self.path, methods=self.methods, endpoint=callback)
        self.server.rules.append(rule)


def _find_free_port():
    """Find a free port to listen on
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port
