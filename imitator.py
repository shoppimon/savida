import os

from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound


class Interceptor(object):
    def __init__(self, app):
        self.url_map = Map([
            Rule('/imitator.py', endpoint=self.intercept)
        ])
        self.app = app

    def intercept(self, request):
        return Response(response='response was intercepted', status=200)

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

# middleware for serving static files
# TODO: let the user choose from what directory static files should be served
not_found_middleware = NotFound()

static_files_middleware = SharedDataMiddleware(not_found_middleware, {
    '/': os.path.dirname(__file__)
})

application = Interceptor(static_files_middleware)

run_simple('127.0.0.1', 5000, application, use_debugger=True, use_reloader=True, threaded=True)
