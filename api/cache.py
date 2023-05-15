import threading
import time


class BookCache:
    def __init__(self, size=3, default_ttl=60):
        self.cache = {}
        self.size = size
        self.default_ttl = default_ttl
        self.access_time = {}
        self.lock = threading.Lock()

    def get_book(self, book_id):
        with self.lock:
            if book_id in self.cache:
                self.access_time[book_id] = time.time()
                return self.cache[book_id]
            else:
                return None

    def add_book(self, book_id, book, ttl=None):
        with self.lock:
            if book_id in self.cache:
                self.access_time[book_id] = time.time()
            else:
                if len(self.cache) >= self.size:
                    oldest_book = min(self.access_time, key=self.access_time.get)
                    del self.cache[oldest_book]
                    del self.access_time[oldest_book]
                self.cache[book_id] = book
                self.access_time[book_id] = time.time()

        if ttl is not None:
            threading.Timer(
                ttl, self.remove_book, args=(book_id, self.access_time[book_id])
            ).start()

    def remove_book(self, book_id: int, periodic_delete_time: float = None):
        with self.lock:
            condition = book_id in self.cache

            # the deal with the case of reentering the book to the cache
            if periodic_delete_time is not None:
                condition = condition and self.access_time[book_id] == periodic_delete_time

            if condition:
                del self.cache[book_id]
                del self.access_time[book_id]

    def clear_cache(self):
        with self.lock:
            self.cache.clear()
            self.access_time.clear()

    def evict_old_books(self):
        with self.lock:
            now = time.time()
            for book_id, access_time in self.access_time.items():
                book_ttl = self.cache.get(book_id, {}).get('ttl', self.default_ttl)
                if now - access_time > book_ttl:
                    del self.cache[book_id]
                    del self.access_time[book_id]
