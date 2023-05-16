from django.test import TestCase
from rest_framework.test import APIClient
from api.models import Book


class EndpointsTesting(TestCase):  # django is creating new DB
    def setUp(self):
        """
        This function defines the client credentials.
        """
        # url const
        self.test_url = f'http://localhost/api/'

        # every test needs a client. APIClient extends Client and allows give credentials.
        self.client_api = APIClient()

        super(EndpointsTesting, self).setUp()

    def test_book_creation(self):
        book_data = {"name": "test", "author": "myself", "pages_amount": 4}
        self.client_api.post(f'{self.test_url}books/', book_data)
        books = Book.objects.all()
        self.assertEqual(len(books), 1)

    def test_book_retrieve(self):
        book_data = {"name": "test", "author": "myself", "pages_amount": 4}
        self.client_api.post(f'{self.test_url}books/', book_data)
        book = Book.objects.first()
        book_id = book.id
        db_book = self.client_api.get(f'{self.test_url}books/{book_id}/')
        self.assertEqual(db_book.data['name'], book_data['name'])

    def test_book_delete(self):
        book_data = {"name": "test", "author": "myself", "pages_amount": 4}
        self.client_api.post(f'{self.test_url}books/', book_data)
        book = Book.objects.first()
        book_id = book.id
        db_book = self.client_api.delete(f'{self.test_url}books/{book_id}/')
        self.assertEqual(Book.objects.first(), None)
