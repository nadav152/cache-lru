from api.models import Book
from typing import Union
import threading
import time
import heapdict


class BookCache:
    def __init__(self, size: int = 3, default_ttl: int = 60):
        self.cache = {}
        self.size = size
        self.default_ttl = default_ttl
        self.access_time = heapdict.heapdict()
        self.lock = threading.Lock()

    def get_book(self, book_id: int) -> Union[Book, None]:
        if book_id in self.cache:
            with self.lock:
                book_access_time = time.time()
                self.access_time[book_id] = book_access_time
            self.__create_delete_timer(book_id, book_access_time)
            return self.cache[book_id]
        else:
            return None

    def add_book(self, book_id: int, book: Book) -> None:
        with self.lock:
            if book_id not in self.cache:
                self.__ensure_cache_size()
                self.cache[book_id] = book

            book_access_time = time.time()
            self.access_time[book_id] = book_access_time
        self.__create_delete_timer(book_id, book_access_time)

    def remove_book(self, book_id: int, periodic_delete_time: float = None) -> None:
        is_delete_from_cache = book_id in self.cache
        with self.lock:
            # the deal with the case of reentering the book to the cache
            if periodic_delete_time is not None:
                is_delete_from_cache = (
                    is_delete_from_cache and self.access_time[book_id] == periodic_delete_time
                )

            if is_delete_from_cache:
                del self.cache[book_id]
                del self.access_time[book_id]

    # not part of requirement but in real life might be needed
    def invalidate_cache(self) -> None:
        with self.lock:
            self.cache.clear()
            self.access_time.clear()

    def __create_delete_timer(self, book_id: int, book_access_time: float) -> None:
        curr_thread = threading.Timer(
            self.default_ttl, self.remove_book, args=(book_id, book_access_time)
        )
        curr_thread.setDaemon(True)
        curr_thread.start()

    def __ensure_cache_size(self) -> None:
        if len(self.cache) >= self.size:
            # this can also be implement with bidirectional linked list to achieve O(1) performance
            # using bidirectional linked list increases the memory usage
            oldest_book_id, oldest_book_time = self.access_time.peekitem()
            del self.cache[oldest_book_id]
            del self.access_time[oldest_book_id]
