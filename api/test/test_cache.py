from django.test import TestCase
from api.models import Book
from api.cache import BookCache
from typing import Union
from threading import Thread
import time


class CacheTesting(TestCase):  # django is creating new DB
    def test_add_get_cache_book(self):
        book_cache = BookCache(size=3, default_ttl=1)
        book_1 = Book.objects.create(name='name', author='me', pages_amount=5)
        book_cache.add_book(book_id=book_1.id, book=book_1)

        # book should be in the cache
        self.assertEqual(book_cache.get_book(book_1.id), book_1)
        time.sleep(2)

        # book should not be in the cache
        self.assertEqual(book_cache.get_book(book_1.id), None)

    def test_remove_cache_book(self):
        book_cache = BookCache(size=3, default_ttl=1)
        book_1 = Book.objects.create(name='name', author='me', pages_amount=5)
        book_cache.add_book(book_id=book_1.id, book=book_1)

        # book should be in the cache
        self.assertEqual(book_cache.get_book(book_1.id), book_1)
        book_cache.add_book(book_id=book_1.id, book=book_1)

        # book should not be in the cache
        book_cache.remove_book(book_id=book_1.id)
        self.assertEqual(book_cache.get_book(book_1.id), None)

    def test_invalidate_cache(self):
        # creating books
        book_cache = BookCache(size=3, default_ttl=60)
        book_1 = Book.objects.create(name='name1', author='me1', pages_amount=1)
        book_2 = Book.objects.create(name='name2', author='me2', pages_amount=2)
        book_cache.add_book(book_id=book_1.id, book=book_1)
        book_cache.add_book(book_id=book_2.id, book=book_2)

        # making sure there book are in the cache
        self.assertEqual(book_cache.get_book(book_1.id), book_1)
        self.assertEqual(book_cache.get_book(book_2.id), book_2)

        # clearing the cache
        book_cache.invalidate_cache()
        self.assertEqual(book_cache.get_book(book_1.id), None)
        self.assertEqual(book_cache.get_book(book_2.id), None)

    def test_spam_cache_book(self):
        # creating books
        book_cache = BookCache(size=3, default_ttl=60)
        info_list = [
            ('name1', 'me1'),
            ('name2', 'me2'),
            ('name3', 'me3'),
            ('name4', 'me4'),
            ('name5', 'me5'),
        ]
        books = [
            Book.objects.create(name=name, author=author, pages_amount=1)
            for name, author in info_list
        ]
        book_cache.add_book(book_id=books[0].id, book=books[0])
        book_cache.add_book(book_id=books[1].id, book=books[1])
        book_cache.add_book(book_id=books[2].id, book=books[2])

        # latest in cache should be the first book
        oldest_book_id, oldest_book_time = book_cache.access_time.peekitem()
        self.assertEqual(oldest_book_id, books[0].id)

        # latest in cache should be the second book
        book_cache.add_book(book_id=books[3].id, book=books[3])
        oldest_book_id, oldest_book_time = book_cache.access_time.peekitem()
        self.assertEqual(oldest_book_id, books[1].id)

        # latest in cache should be the third book
        book_cache.add_book(book_id=books[4].id, book=books[4])
        oldest_book_id, oldest_book_time = book_cache.access_time.peekitem()
        self.assertEqual(oldest_book_id, books[2].id)

    def test_concurrent_access(self):
        def get_book_from_cache(book_id: int, result_holder: list) -> Union[Book, None]:
            result = book_cache.get_book(book_id)
            result_holder[0] = result
            return result

        def delete_book_from_cache(book_id: int) -> None:
            book_cache.remove_book(book_id)

        result_holder = ["not None"]
        book_cache = BookCache(size=3, default_ttl=1)
        book_1 = Book.objects.create(name='name', author='me', pages_amount=5)
        book_cache.add_book(book_id=book_1.id, book=book_1)

        # Create threads for getting and deleting from the cache
        delete_thread = Thread(target=delete_book_from_cache, args=(book_1.id,))
        get_thread = Thread(target=get_book_from_cache, args=(book_1.id, result_holder))

        # Start the threads concurrently
        delete_thread.start()
        get_thread.start()
        get_thread.join()
        delete_thread.join()

        self.assertEqual(result_holder[0], None)
