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

    def __call__(self, environ, start_response):
        # try to match URL from url_map
        request = Request(environ)
        adapter = self.url_map.bind_to_environ(request)

        try:
            endpoint, values = adapter.match()
            response = endpoint(request, **values)
            return response(environ, start_response)
        except HTTPException as error:
            # if none of the urls matched, delegate the request to next middleware
            return self.app(environ, start_response)


class Interceptor(object):
    def __init__(self):
        self.paths = []
        self.rules = []

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

    def start(self, static_dir=None):
        not_found_middleware = NotFound()

        print static_dir, os.path.dirname(__file__)
        # middleware for serving static files
        static_files_middleware = SharedDataMiddleware(not_found_middleware, {
            '/': static_dir or os.path.dirname(__file__)
        })

        wsgi_application = WSGIApplication(static_files_middleware)

        # plug the rules
        wsgi_application.url_map = Map(self.rules)
        run_simple('127.0.0.1', 5000, wsgi_application, use_debugger=True, use_reloader=True, threaded=True)

    def wait(self, seconds):
        # server_instance.when('/some/path').wait(seconds=5)
        def callback(request):
            time.sleep(seconds)
            # raise exception so that the static middleware will handle this request
            raise NotFound()

        path = self.paths.pop()
        self.rules.append(Rule(path, endpoint=callback))

