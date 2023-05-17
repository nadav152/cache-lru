from typing import Optional, Any
import threading
import time
import heapdict


class Cache:
    """
    This cache class supports saving DB models objects or object with ID
    :param size: will set the cache size.
    :param default_ttl: will set the TTL for objects in the cache.
    """

    def __init__(self, size: int = 3, default_ttl: int = 60):
        self.cache = {}
        self.size = size
        self.default_ttl = default_ttl
        self.access_time = heapdict.heapdict()
        self.lock = threading.Lock()

    def get_object(self, object_id: int) -> Optional[Any]:
        if object_id in self.cache:
            with self.lock:
                object_access_time = time.time()
                self.access_time[object_id] = object_access_time
            self.__create_delete_timer(object_id, object_access_time)
            return self.cache[object_id]
        else:
            return None

    def set_object(self, object_id: int, object_model: Any) -> None:
        with self.lock:
            if object_id not in self.cache:
                self.__ensure_cache_size()
                self.cache[object_id] = object_model

            object_access_time = time.time()
            self.access_time[object_id] = object_access_time
        self.__create_delete_timer(object_id, object_access_time)

    def remove_object(self, object_id: int, periodic_delete_time: float = None) -> None:
        is_delete_from_cache = object_id in self.cache
        with self.lock:
            # the deal with the case of reentering the same object to the cache
            if periodic_delete_time is not None:
                is_delete_from_cache = (
                    is_delete_from_cache and self.access_time[object_id] == periodic_delete_time
                )

            if is_delete_from_cache:
                del self.cache[object_id]
                del self.access_time[object_id]

    # not part of requirement but in real life might be needed
    def invalidate_cache(self) -> None:
        with self.lock:
            self.cache.clear()
            self.access_time.clear()

    def __create_delete_timer(self, object_id: int, object_access_time: float) -> None:
        curr_thread = threading.Timer(
            self.default_ttl, self.remove_object, args=(object_id, object_access_time)
        )
        curr_thread.setDaemon(True)
        curr_thread.start()

    def __ensure_cache_size(self) -> None:
        if len(self.cache) >= self.size:
            # this can also be implement with bidirectional linked list to achieve O(1) performance
            # using bidirectional linked list increases the memory usage
            oldest_object_id, oldest_object_time = self.access_time.peekitem()
            del self.cache[oldest_object_id]
            del self.access_time[oldest_object_id]
