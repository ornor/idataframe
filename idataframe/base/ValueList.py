from __future__ import annotations
from typing import Any, List

from idataframe.base.Value import Value

__all__ = ['ValueList']



class ValueList():
    """
    List of Values objects.
    """
    def __init__(self):
        self._value_items = []

    def add(self, value:Value) -> ValueList:
        if not isinstance(value, Value):
            raise TypeError("value_messages attribute must be a Value object (now value_messages type is {})".format(type(value)))

        self._value_items.append(value)
        return

    @property
    def items(self) -> List[Value]:
        return self._value_items

    @items.setter
    def items(self, _):
        raise PermissionError("The items property is read only")

    @property
    def values(self) -> List[Any]:
        return [v.value for v in self._value_items if v.value is not None]

    @values.setter
    def values(self, _):
        raise PermissionError("The values property is read only")

    @property
    def messages(self) -> List[Any]:
        "Concaternate messages of objects."
        messages_list = []
        for v in self._value_items:
            messages_list = messages_list + v.messages
        return messages_list

    @messages.setter
    def messages(self, _):
        raise PermissionError("The messages property is read only")

