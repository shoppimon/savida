Savida Testing Web Server Fixture
=================================
Savida is a testing-oriented HTTP server wrapper. It allows to easily
launch a Web server during an automated test, define its behavior (i.e.
how to respond to different requests) and shut it down easily when the
test ends.

This is useful when testing complex HTTP-client based systems - for
example at Shoppimon it is used to test our Web monitoring system
infrastructure, which needs to access Websites using a complex browser
and return different information based on entire page behaviors or even
entire passes through the site.

Testing such systems is not possible using current mock HTTP client
libraries or naive test server implementations, and this is why we
created Savida.

Note that while the examples below refer to `py.test`, this module is in
no way tied to a specific testing framework or methodology.

# Usage
In testing frameworks like `py.test`, usage usually looks something like:

    from savida.fixture import http_server

    def test_my_browser_works():
        # Set up the server with a static document root directory
        with http_server(document_root='fixtures/webroot') as server:

            # Return 404 on /js/main.js even if it exists in our docroot
            server.when('/js/main.js').response(
                status=404, response='Gone to Lunch')

            # Wait 10 seconds before responding to /slow.php
            server.when('/slow.php').wait(10)

            server.start()

            response = requests.get(server.url + '/js/main.js')
            assert response.status_code == 404


## Usage in module setup / teardown functions
TBD

# API
TBD

# TODO
* Add documentation
* Clean up API, replace `wait` method with something more concise
* Add support for matching based on HTTP method

# License
Copyright (c) 2017 Shoppimon LTD

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
