"""Server wrapper for Savida
"""

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
        self.paths = []
        self.rules = []
        self.document_root = document_root
        self.host = '127.0.0.1'
        self.port = _find_free_port()

    def when(self, path):
        self.paths.append(
            path
        )

        return self

    def call(self, callback):
        path = self.paths.pop()

        def callback_wrapper(request):
            response = callback(request)

            # pass request to static middleware by raising NotFound
            if not response:
                raise NotFound()

            # otherwise, return the response
            return response

        self.rules.append(Rule(path, endpoint=callback_wrapper))

    def times(self, callback, times_to_call):
        path = self.paths.pop()

        def callback_wrapper(*args, **kwargs):
            # if callback called reached, let static middleware handle the request
            if callback_wrapper.calls_made >= callback_wrapper.times_to_call:
                raise NotFound()
            else:
                response = callback(*args, **kwargs)
                callback_wrapper.calls_made += 1

            # let static middleware handle the request by raising NotFound
            if not response:
                raise NotFound()

            # otherwise, return the response
            return response

        callback_wrapper.calls_made = 0
        callback_wrapper.times_to_call = times_to_call
        self.rules.append(Rule(path, endpoint=callback_wrapper))

    def response(self, *args, **kwargs):
        """Set the exact response to return when a certain URL is requested
        """
        # server_instance.when('/some/path').response(status=404, response='im 404')
        # pass same parameters as Response() expects
        # we should return Response() object
        def response_wrapper(_):
            return Response(*args, **kwargs)

        path = self.paths.pop()
        self.rules.append(Rule(path, endpoint=response_wrapper))

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


        """
        """

    def wait(self, seconds):
        # server_instance.when('/some/path').wait(seconds=5)
        def callback(request):
            time.sleep(seconds)
            # raise exception so that the static middleware will handle this request
            raise NotFound()

        path = self.paths.pop()
        self.rules.append(Rule(path, endpoint=callback))

def _find_free_port():
    """Find a free port to listen on
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port
