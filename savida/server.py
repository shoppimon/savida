"""
TODO:
    (1) the server is running on main thread, currently there is no way to stop it programatically.

        Werkzeug provides a way to shutdown werkzeug server:
        http://werkzeug.pocoo.org/docs/0.11/serving/#shutting-down-the-server

        Basically, it is possible to configure a Rule that when invoked will terminate Werzkzeug:

        (WSGIApplication)
        self.url_map = Map([
            Rule('/shutdown', endpoint=self.shutdown)
        ])

        def shutdown(self, request):
            shutdown_func = request.environ.get('werkzeug.server.shutdown', None)
            if not shutdown_func:
                raise RuntimeError('Not running with the Werkzeug Server')
            shutdown_func()

        in this case, making GET on `/shutdown` will invoke the werkzeug shutdown function.

        NOTE 1: this only works on development server.
        NOTE 2: multithreading still needed.

    (2) the web server does not look for available free port that it can use,
        currently port is hardcoded.

    See example.py for usage example.
"""
import os

from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
import time


class WSGIApplication(object):

    def __init__(self, app):
        self.url_map = Map([])
        self.app = app

    def shutdown_server(self, environ):
        if not 'werkzeug.server.shutdown' in environ:
            raise RuntimeError('Not running the development server')
        environ['werkzeug.server.shutdown']()

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
        self.base_url = 'http://127.0.0.1:5000'

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
        # server_instance.when('/some/path').response(status=404, response='im 404')
        # pass same parameters as Response() expects
        # we should return Response() object
        def response_wrapper(request):
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

        run_simple('127.0.0.1', 5000, self._app, threaded=True)

    def stop(self):
        """
        Not Implemented.
        """
        pass

    def wait(self, seconds):
        # server_instance.when('/some/path').wait(seconds=5)
        def callback(request):
            time.sleep(seconds)
            # raise exception so that the static middleware will handle this request
            raise NotFound()

        path = self.paths.pop()
        self.rules.append(Rule(path, endpoint=callback))
