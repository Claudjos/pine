import unittest
from ddt import ddt, file_data
from pine.testing import PineClient
from examples.books import app
from json import dumps, loads


client = PineClient(app)


@ddt
class TestCases(unittest.TestCase):

	@file_data("data.yaml")
	def test_request(self, request, response):
		
		if "body" in request:
			if isinstance(request["body"], (dict, list)):
				request["body"] = dumps(request["body"]).encode()
			elif isinstance(request["body"], str):
				request["body"] = request["body"].encode()
			else:
				raise ValueError("Invalid type for request body.\
					Accepted type are: str, list and dict")
		
		res = client.request(**request)
		
		if "status" in response:
			assert res.status_code == response["status"]
		if "headers" in response:
			assert res.headers == response["headers"]
		if "body" in response:
			if isinstance(response["body"], str):
				assert response["body"] == res.text
			else:
				assert response["body"] == res.json
