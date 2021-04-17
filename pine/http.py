"""
This module provides a very simple abstraction for HTTP
requests and responses, with methods to parse/convert
messages from/to wsgi format.
"""

from json import loads, dumps
from urllib.parse import parse_qs
from typing import Iterator
from types import GeneratorType
from fir import http, wsgi


class HTTPMessage(http.Message):

	def set_body(self, value):
		if isinstance(value, (list, dict)):
			value = dumps(value)
			self.headers.setdefault("content-type", "application/json")
		super().set_body(value)

	@property
	def content_type(self):
		return self.headers.get("content-type", None)

	@property
	def json(self):
		return self.get_json()

	@property
	def text(self):
		return self.get_body().decode()

	@property
	def form(self):
		return parse_qs(self.body.decode())


class Response(HTTPMessage, http.Response):

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


class Request(HTTPMessage, http.Request):

	@classmethod
	def from_wsgi(cls, environ: dict):
		return wsgi.environ_to_request(environ, cls)
