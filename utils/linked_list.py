from typing import Optional, Any


class Node:
    def __init__(self, value: Any, creation_time: float):
        self.value = value
        self.creation_time = creation_time
        self.prev = None
        self.next = None


class BidirectionalLinkedList:
    """
    This is bidirectional linked list class.
    The class supports all linked list actions in O(1) operations.
    With help of this class we can manage an LRU cache for saving any object.
    """

    def __init__(self):
        self.head = None
        self.node_dict = {}

    def add_node(self, value: Any, creation_time: float, id_key: int) -> None:
        new_node = Node(value, creation_time)
        new_node.value = value
        self.node_dict[id_key] = new_node

        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node

    def remove_node(self, id_key: int) -> None:
        if id_key not in self.node_dict:
            return
        node = self.node_dict[id_key]
        prev_node = node.prev
        next_node = node.next

        # handling all the cases of last/first/middle/tail/head
        if prev_node:
            prev_node.next = next_node
        else:
            self.head = next_node

        if next_node:
            next_node.prev = prev_node
        else:
            self.tail = prev_node

        del self.node_dict[id_key]

    def get_head(self) -> Node:
        if self.head is None:
            return None
        return self.head

    def get_node(self, id_key: int) -> Optional[Node]:
        if id_key in self.node_dict:
            return self.node_dict[id_key]

        return None

    def clear(self) -> None:
        self.head = None
        self.tail = None
        self.node_dict.clear()
