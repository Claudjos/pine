from .core import App
from .http import Request
from io import BytesIO
from typing import Union
from types import GeneratorType
from urllib.parse import urlparse


class PineClient:

	def __init__(self, app: App):
		self.app = app

	def request(self, method: str, url: str, headers: dict = None, 
		body: Union[bytes, str] = None):
		if headers is None:
			headers = {}
		if body is None:
			body = b''
		if isinstance(body, str):
			body = body.encode()
		parsed = urlparse(url)
		environ = {
			"wsgi.input": BytesIO(body),
			"REQUEST_METHOD": method,
			"PATH_INFO": parsed.path,
			"RAW_URI": url,
			"QUERY_STRING": parsed.query,
		}
		for header in headers:
			key = "HTTP_{}".format(header.upper().replace("-", "_"))
			environ[key] = headers[header]
		if body != b'':
			environ["CONTENT_LENGTH"] = len(body)
		response = self.app.process(environ, Request.from_wsgi(environ))
		if isinstance(response.body, GeneratorType):
			response.body = b"".join(response.body)
		if isinstance(response.body, str):
			response.body = response.body.encode()
		return response