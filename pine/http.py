"""
This module provides a very simple abstraction for HTTP
requests and responses, with methods to parse/convert
messages from/to wsgi format.
"""

from json import loads, dumps
from urllib.parse import parse_qs
from typing import Iterator
from types import GeneratorType
from fir import http


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
		return loads(self.text)

	@property
	def text(self):
		return self.get_body().decode()

	@property
	def form(self):
		return parse_qs(self.body.decode())


class Response(HTTPMessage, http.Response):

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

	def __init__(self, status_code: int = 200, status_message: str = None, 
		headers: dict = None, body: bytes = None
	):
		if status_message is None:
			status_message = self.STATUS_MESSAGES.get(status_code, " ")
		super().__init__(status_code, status_message, headers, body)

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
			uri=environ["RAW_URI"],
			headers=headers,
			body=environ['wsgi.input'].read(request_body_size)
		)
