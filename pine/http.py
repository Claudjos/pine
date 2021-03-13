"""
This module provides a very simple abstraction for HTTP
requests and responses, with methods to parse/convert
messages from/to wsgi format.
"""

from json import loads, dumps
from urllib.parse import parse_qs
from typing import Iterator
from types import GeneratorType


class HTTPMessage:

	def __init__(self, version = "HTTP/1.1", headers = None, body = None):
		self.version = version
		self.headers = headers if headers is not None else {}
		self.body = body if body is not None else b''
		if isinstance(self.body, (str)):
			self.body = self.body.encode()
		if isinstance(self.body, (dict, list)):
			self.body = dumps(self.body).encode()
			self.headers.setdefault("content-type", "application/json")

	@property
	def version(self):
		return self._version

	@version.setter
	def version(self, value):
		self._version = value
	
	@property
	def headers(self):
		return self._headers

	@headers.setter
	def headers(self, value):
		self._headers = value

	@property
	def body(self):
		return self._body

	@body.setter
	def body(self, value):
		self._body = value

	@property
	def content_type(self):
		return self._headers.get("content-type", None)

	@property
	def json(self):
		return loads(self.body)

	@property
	def text(self):
		if isinstance(self.body, bytes):
			return self.body.decode()
		elif isinstance(self.body, str):
			return self.body
		else:
			raise ValueError("Body must be instance of bytes or str to use this method")

	@property
	def form(self):
		return parse_qs(self.body.decode())


class Response(HTTPMessage):

	STATUS_MESSAGES = {
		200: "OK",
		201: "Created",
		204: "No Content",
		301: "Moved Permanently",
		302: "Found",
		401: "Unauthorized",
		403: "Forbidden",
		404: "Not Found",
		405: "Method Not Allowed",
		500: "Internal Server Error"
	}

	def __init__(self, status_code=200, status_message=None, **kwargs):
		super().__init__(**kwargs)
		self.status_code = status_code
		self.status_message = status_message if status_message is not None else Response.STATUS_MESSAGES.get(status_code, "")

	@property
	def response_line(self):
		return f"{self.version} {self.status_code} {self.status_message}"
	
	@property
	def status_message(self):
		return self._status_message

	@status_message.setter
	def status_message(self, value):
		self._status_message = value

	@property
	def status_code(self):
		return self._status_code

	@status_code.setter
	def status_code(self, value):
		self._status_code = value

	@property
	def wsgi_body(self):
		"""
		Returns the body in the wsgi format.
		"""
		if isinstance(self.body, str):
			return [self.body.encode()]
		elif isinstance(self.body, bytes):
			return [self.body]
		elif isinstance(self.body, GeneratorType):
			return self.body
		else:
			raise ValueError("Response body must be str, bytes or generator.")
	
	@staticmethod
	def stream(data: Iterator):
		"""
		Cast the values of an iterator object to bytes.
		"""
		def x():
			for chunk in data:
				if isinstance(chunk, str):
					yield chunk.encode()
				elif isinstance(check, bytes):
					yield chunk
				else:
					raise ValueError("Iterator must yield either str or bytes.")
			return
		return x()


class Request(HTTPMessage):
	
	def __init__(self, method, uri, raw_uri, raw_query, **kwargs):
		super().__init__(**kwargs)
		self.method = method
		self.uri = uri
		self.raw_uri = raw_uri
		self.query_params = parse_qs(raw_query)

	@property
	def request_line(self):
		return f"{self.method} {self.raw_uri} {self.version}"

	@property
	def uri(self):
		return self._uri
	
	@uri.setter
	def uri(self, value):
		self._uri = value

	@property
	def raw_uri(self):
		return self._raw_uri

	@raw_uri.setter
	def raw_uri(self, value):
		self._raw_uri = value

	@property
	def route_params(self):
		return self._route_params

	@route_params.setter
	def route_params(self, value):
		self._route_params = value

	@property
	def query_params(self):
		return self._query_params

	@query_params.setter
	def query_params(self, value):
		self._query_params = value

	@property
	def method(self):
		return self._method

	@method.setter
	def method(self, value):
		self._method = value

	@classmethod
	def from_wsgi(cls, environ: dict):
		"""
		Build a Request instance from a wsgi environ.
		"""
		headers = {}
		for key in environ:
			if key.startswith("HTTP_"):
				headers[key.replace("HTTP_", "").replace("_", "-").lower()] = environ[key]
		try:
			request_body_size = int(environ.get('CONTENT_LENGTH', 0))
		except (ValueError):
			request_body_size = 0
		return cls(
			method=environ["REQUEST_METHOD"].upper(),
			uri=environ["PATH_INFO"],
			raw_uri=environ["RAW_URI"],
			raw_query=environ["QUERY_STRING"],
			headers=headers,
			body=environ['wsgi.input'].read(request_body_size)
		)
