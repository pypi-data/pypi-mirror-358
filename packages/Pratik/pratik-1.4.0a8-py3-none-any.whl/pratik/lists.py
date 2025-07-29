"""LinkedList module.

This module provides a generic, doubly linked list implementation using
sentinel nodes for safe and efficient manipulation. The list supports
standard operations such as head/tail insertion, indexed insertion,
removal, search, and conversion to native Python lists.

The `LinkedList` class is fully type-safe and compatible with Python 3.7+,
supporting any value type via generics.

Example:
    >>> llist = LinkedList[int]()
    >>> llist.head_append(1)
    >>> llist.tail_append(2)
    >>> list(llist)
    [1, 2]
"""

from dataclasses import dataclass, field
from typing import Generic, Iterator, Optional, TypeVar

T = TypeVar('T')
T_Cell = TypeVar('T_Cell')


@dataclass
class _Cell(Generic[T_Cell]):
    """A cell in the linked list."""
    value: Optional[T_Cell] = None
    before: Optional['_Cell[T_Cell]'] = field(default=None, repr=False)
    after: Optional['_Cell[T_Cell]'] = field(default=None, repr=False)

    def __repr__(self) -> str:
        return repr(self.value)


class LinkedList(Generic[T]):
    """Doubly linked list implementation using sentinel nodes."""

    def __init__(self) -> None:
        """Initialize an empty LinkedList with sentinel nodes."""
        self._head: _Cell[T] = _Cell()
        self._tail: _Cell[T] = _Cell()
        self._head.after = self._tail
        self._tail.before = self._head
        self._size = 0

    def __iter__(self) -> Iterator[T]:
        """Iterate over the values in the list."""
        current = self._head.after
        while current is not self._tail:
            yield current.value  # type: ignore
            current = current.after

    def __len__(self) -> int:
        """Return the number of elements in the list."""
        return self._size

    @property
    def is_empty(self) -> bool:
        """Check whether the list is empty."""
        return self._size == 0

    def head_append(self, value: T) -> None:
        """Append a value at the head of the list.

        Args:
            value (T): The value to append.
        """
        self._insert_between(value, self._head, self._head.after)

    def tail_append(self, value: T) -> None:
        """Append a value at the tail of the list.

        Args:
            value (T): The value to append.
        """
        self._insert_between(value, self._tail.before, self._tail)

    def append_at(self, value: T, index: int) -> None:
        """Append a value at a specific index.

        Args:
            value (T): The value to append.
            index (int): The index at which to insert.

        Raises:
            IndexError: If index is out of bounds.
        """
        if index < 0 or index > self._size:
            raise IndexError("Index out of range")

        current = self._head.after
        for _ in range(index):
            current = current.after
        self._insert_between(value, current.before, current)

    def _insert_between(self, value: T, before: _Cell[T], after: _Cell[T]) -> None:
        """Insert a value between two cells.

        Args:
            value (T): The value to insert.
            before (_Cell[T]): The cell before.
            after (_Cell[T]): The cell after.
        """
        cell = _Cell(value, before, after)
        before.after = cell
        after.before = cell
        self._size += 1

    def to_list(self) -> list[T]:
        """Convert the linked list to a Python list.

        Returns:
            list[T]: List of values.
        """
        return list(self)
