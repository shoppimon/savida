import BaseHTTPServer
import os
import shutil
import time


# def server_py_handler(request):
#     with open(os.getcwd() + request.path, 'rb') as f:
#         request.send_response(code=200)
#         request.send_header('Content-type', 'text/plain')
#         request.end_headers()
#
#         time.sleep(10)
#         shutil.copyfileobj(f, request.wfile)


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        print self.path
        # code that serves static files goes here
        with open(os.getcwd() + self.path, 'rb') as f:
            self.send_response(code=200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            shutil.copyfileobj(f, self.wfile)


# class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
#     def do_GET(self): server_py_handler(self)

def response_500(context):
    context.send_response(code=500)


def sleep():
    time.sleep(2)



server_address = ('', 8000)
httpd = BaseHTTPServer.HTTPServer(server_address, RequestHandler)
print 'Running on {server_address}'.format(server_address=server_address)
httpd.serve_forever()


