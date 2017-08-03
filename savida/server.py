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
import ssl

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


class DelayedWSGIApplication(WSGIApplication):

    def __init__(self, app, delay_time):
        super(DelayedWSGIApplication, self).__init__(app)
        self.delay_time = delay_time

    def __call__(self, environ, start_response):
        # try to match URL from url_map
        request = Request(environ)
        adapter = self.url_map.bind_to_environ(request)

        time.sleep(self.delay_time)

        try:
            endpoint, values = adapter.match()
            response = endpoint(request, **values)
            return response(environ, start_response)
        except HTTPException:
            # if none of the urls matched, delegate to next middleware
            return self.app(environ, start_response)


class Server(object):

    def __init__(self, document_root=None, ssl_key=None, ssl_cert=None, ssl_encryption=False, delayed_response=None):
        self._app = None
        self.rules = []
        self.document_root = document_root
        self.host = '127.0.0.1'
        self.port = _find_free_port()
        self.ssl_encryption = ssl_encryption
        self.ssl_key = ssl_key
        self.ssl_cert = ssl_cert
        self.delayed_response = delayed_response

    def when(self, path, methods=None):
        rule = RuleMaker(self, path, methods)
        return rule

    def start(self):
        middleware = NotFound()
        if self.document_root:
            # middleware for serving static files
            middleware = SharedDataMiddleware(middleware,
                                              {"/": self.document_root})

        if self.delayed_response:
            self._app = DelayedWSGIApplication(middleware, self.delayed_response)
        else:
            self._app = WSGIApplication(middleware)

        # plug the rules
        self._app.url_map = Map(self.rules)

        if self.ssl_encryption:
            try:
                ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
                ctx.load_cert_chain(self.ssl_cert, self.ssl_key)
                run_simple(self.host, self.port, self._app, threaded=True, ssl_context=ctx)
            except TypeError:
                pass
        else:
            run_simple(self.host, self.port, self._app, threaded=False)

    @property
    def base_url(self):
        if self.port is None:
            raise RuntimeError("Server was not started, base_url is unknown")
        if self.ssl_encryption:
            return 'https://{}:{}'.format(self.host, self.port)
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

    def redirect(self, location, code=302):
        """Redirect to a given location
        """
        def f(_):
            response = Response('<p>Redirected to {}, HTTP Status code: {}</p>'.format(location, code), mimetype='text/html')
            response.headers['Location'] = location
            return response
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
