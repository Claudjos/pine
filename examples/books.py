from pine import *
from json import dumps


app = App()


class Library:

	def __init__(self):
		self._pk = 0
		self._library = {}

	def get_books(self):
		for book in self._library:
			yield self._library[book]
		return

	def get_book(self, key: int) -> dict:
		return self._library[key]

	def create_book(self, book: dict) -> int:
		self._pk += 1
		self._library[self._pk] = book
		return self._pk

	def insert_or_replace_book(self, book_id: int, book: dict):
		self._library[book_id] = book

	def update_book(self, book_id: int, title: str = None, author: str = None):
		if title is not None:
			self._library[book_id]["title"] = title
		if author is not None:
			self._library[book_id]["author"] = author

	def delete_book(self, book_id: int):
		del self._library[book_id]


library = Library()


@app.route("/books")
class Books(RequestHandler):

	def get(self):
		def x(books):
			for book in books:
				yield "event: book\n"
				yield "data: {}\n\n".format(dumps(book))
			return
		return Response(
			body=Response.stream(x(library.get_books())),
			headers={
				"content-type": "text/event-stream"
			}
		)

	def post(self):
		_id = library.create_book(self.request.json)
		return Response(status_code=201, body={"book_id": _id})

	def options(self):
		return Response()


@app.route("/books/<book_id>")
class Books(RequestHandler):

	@property
	def book_id(self):
		return int(self.request.route_params["book_id"])

	def handle_key_error(f):
		def wrapper(self):
			try:
				return f(self)
			except KeyError:
				return Response(status_code=404)
		return wrapper

	@handle_key_error
	def get(self):
		book = library.get_book(self.book_id)
		return Response(body=book)

	def put(self):
		if self.request.content_type != "application/json":
			return Response(status_code=400)
		else:
			library.insert_or_replace_book(self.book_id, self.request.json)
			return Response()

	@handle_key_error
	def patch(self):
		form = self.request.form
		title = form.get("title", [None])[0]
		author = form.get("author", [None])[0]
		library.update_book(self.book_id, title=title, author=author)
		return Response()

	def options(self):
		return Response()

	@handle_key_error
	def delete(self):
		library.delete_book(self.book_id)
		return Response()
