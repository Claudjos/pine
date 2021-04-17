"""
This module is the core of the web framework. It defines
classes to route and handle requests, and deal with the
gateway interface.
"""

import re
from typing import Callable
from .http import Request, Response


class RequestHandler:
	"""
	RequestHandlers handle single HTTP requests. They are created
	and invoked by the Router.
	"""

	def __init__(self, environ: dict, request: Request):
		self.environ = environ
		self.request = request

	def process(self) -> Response:
		if self.request.method.upper() == "HEAD":
			return self.head()
		elif self.request.method.upper() == "GET":
			return self.get()
		elif self.request.method.upper() == "PUT":
			return self.put()
		elif self.request.method.upper() == "POST":
			return self.post()
		elif self.request.method.upper() == "PATCH":
			return self.patch()
		elif self.request.method.upper() == "OPTIONS":
			return self.options()
		elif self.request.method.upper() == "DELETE":
			return self.delete()
		elif self.request.method.upper() == "CONNECT":
			return self.connect()
		else:
			return Response(status_code=405)

	def options(self):
		return Response(status_code=405)

	def head(self):
		return Response(status_code=405)

	def get(self):
		return Response(status_code=405)

	def post(self):
		return Response(status_code=405)

	def patch(self):
		return Response(status_code=405)

	def put(self):
		return Response(status_code=405)

	def delete(self):
		return Response(status_code=405)

	def connect(self):
		return Response(status_code=405)


class NotFoundHandler(RequestHandler):
	"""
	This is the default RequestHandler used by the Router
	when no handler is found for the requested URI.
	"""

	def process(self):
		return Response(status_code=404)


class Router:
	"""
	Router keeps track of RequestHandlers and the URIs they're
	meant to serve. It also enriches the HTTP request with the
	route parameters.
	"""

	def __init__(self, not_found_handler = NotFoundHandler):
		self._rules = list()
		self._find_params_names_regex = re.compile(r"<(\w*?)>")
		self.not_found_handler = not_found_handler

	@property
	def not_found_handler(self):
		return self._not_found_handler
	
	@not_found_handler.setter
	def not_found_handler(self, handler):
		self._not_found_handler = handler

	def add_handler(self, path: str, handler: RequestHandler) -> None:
		params_names = self._find_params_names_regex.findall(path)
		route_match_regex = re.compile(self._find_params_names_regex.sub("(.*?)", path) + "$")
		self._rules.append((route_match_regex, handler, params_names))

	def get_handler(self, request: Request) -> RequestHandler:
		for rule in self._rules:
			result = rule[0].match(request.path)
			if result is not None:
				request.route_params = dict(zip(rule[2], result.groups()))
				return rule[1]
		return self.not_found_handler


class App:
	"""
	App deals with wsgi (or other gateway interfaces). Just one instance
	of this class exists in a Web Application. This class is invoked by the
	web server, and by the use of a router, retrieves the RequestHandlers
	and serve the requests.
	"""

	def __init__(self, router: Router = None):
		if router is None:
			router = Router()
		self._router = router

	def __call__(self, environ, start_response):
		return self.wsgi(environ, start_response)

	def wsgi(self, environ, start_response):
		request = Request.from_wsgi(environ)
		response = self.process(environ, request)
		start_response(
			f"{response.status_code} {response.status_message}",
			response.headers.items()
		)
		return response.wsgi_body

	@property
	def router(self):
		return self._router
	
	def route(self, path: str) -> Callable:
		def wrapper(klass: RequestHandler) -> RequestHandler:
			self.router.add_handler(path, klass)
		return wrapper

	def process(self, environ: dict, request: Request) -> Response:
		return self.router.get_handler(request)(environ, request).process()
