import os

from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound


class App(object):
    def __init__(self):
        self.url_map = Map([
            Rule('/css/normalize.css', endpoint='root_handler')
        ])

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, endpoint)(request, **values)
        except HTTPException, e:
            return e

    def wsgi_app(self, environ, start_response):
        # return Response(<response>)(environ, start_response)
        request = Request(environ)
        response = self.dispatch_request(request)

        return response(environ, start_response)

    # endpoint (handler)
    def root_handler(self, request):
        print "root_handler"
        return Response(response='Hi man', status=200)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

app = App()

# middleware
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/': os.path.join(os.path.dirname(__file__), 'static')
})

run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)
