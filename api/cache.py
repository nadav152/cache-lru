from typing import Optional, Any
from utils.linked_list import BidirectionalLinkedList
import threading
import time



class Cache:
    """
    This cache class supports saving DB models objects or object with ID
    :param size: will set the cache size.
    :param default_ttl: will set the TTL for objects in the cache.
    """

    def __init__(self, size: int = 3, default_ttl: int = 60):
        self.size = size
        self.default_ttl = default_ttl
        self.cache_linked_list = BidirectionalLinkedList()
        self.lock = threading.Lock()

    def get_object(self, object_id: int) -> Optional[Any]:
        if object_id in self.cache_linked_list.node_dict:
            with self.lock:
                # re-entering node to renew its TTL
                object_access_time = time.time()
                curr_node = self.cache_linked_list.get_node(object_id)
                self.cache_linked_list.remove_node(object_id)
                model_object = curr_node.value
                self.cache_linked_list.add_node(model_object, object_access_time, model_object.id)

            self.__create_delete_timer(object_id, object_access_time)
            return curr_node.value
        else:
            return None

    def set_object(self, object_id: int, model_object: Any) -> None:
        with self.lock:
            object_access_time = time.time()
            if object_id not in self.cache_linked_list.node_dict:
                self.__ensure_cache_size()
                self.cache_linked_list.add_node(model_object, object_access_time, object_id)

        self.__create_delete_timer(object_id, object_access_time)

    def remove_object(self, object_id: int, periodic_delete_time: float = None) -> None:
        in_cache = object_id in self.cache_linked_list.node_dict
        with self.lock:
            # the deal with the case of reentering the object to the cache
            if periodic_delete_time is not None and in_cache:
                curr_node = self.cache_linked_list.get_node(object_id)
                object_access_time = curr_node.creation_time
                in_cache = in_cache and object_access_time == periodic_delete_time

            if in_cache:
                self.cache_linked_list.remove_node(object_id)

    # not part of requirement but in real life might be needed
    def invalidate_cache(self) -> None:
        with self.lock:
            self.cache_linked_list.clear()

    def __create_delete_timer(self, object_id: int, object_access_time: float) -> None:
        curr_thread = threading.Timer(
            self.default_ttl, self.remove_object, args=(object_id, object_access_time)
        )
        curr_thread.setDaemon(True)
        curr_thread.start()

    def __ensure_cache_size(self) -> None:
        if len(self.cache_linked_list.node_dict) >= self.size:
            oldest_node = self.cache_linked_list.get_head()
            object_id = oldest_node.value.id
            self.cache_linked_list.remove_node(object_id)
