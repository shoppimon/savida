from savida.server import Server
from werkzeug.wrappers import Response

"""
    Functions have to return werkzeug's Response (http://werkzeug.pocoo.org/docs/0.11/wrappers/) object OR
    raise an error, i.e `raise NotFound`if you want to pass the request to the next middleware, in our case,
    it is the `static_files_middleware`
"""

http_server = Server(static_dir='/home/vladimir/Shoppimon/web-server-imitator/static2')

# respond with custom status and response
http_server.when('/js/main.js').response(status=404, response='Gone to Lunch')

# wait 5 seconds and then return the file
http_server.when('/css/normalize.css').wait(seconds=5)

# call a function expectation match

http_server.when('/css/main.css').call(lambda request: Response(status=200, response='OK'))

# call a function each time for n times when expectation match and then fallback to returning static file
http_server.when('/js/plugins.js').times(lambda request: Response(status=200, response='Understood'), 3)

# serve directory of static files
http_server.start()
