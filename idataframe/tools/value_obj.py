from __future__ import annotations
from typing import Any, Generic, TypeVar, Callable, List, Tuple
import sys

import numpy as np
import pandas as pd

from idataframe.tools import list_remove_duplicates

__all__ = ['str_na', 'int_na', 'float_na', 'is_na',
           'Value', 'ValueList']


# -----------------------------------------------------------------------------


str_na = str(pd.NA)
int_na = -sys.maxsize
float_na = np.nan
series_na = pd.NA


def is_na(value:str|int|float|Value) -> bool:
    if isinstance(value, str):
        return value == str_na
    elif isinstance(value, int):
        return value == int_na
    elif isinstance(value, float):
        return np.isnan(value)
    elif isinstance(value, Value):
        return value.value is None
    else:
        return np.isnan(value) or pd.isna(value)


# -----------------------------------------------------------------------------


T = TypeVar("T")
U = TypeVar("U")


class Value(Generic[T]):
    """
    Kind of monad type containing a value and (optional) multiple text messages.

    Based on: https://github.com/ArjanCodes/examples/blob/main/2023/monad/maybe_railroad_v2.py


    only_value = Value(123)
    only_message = Value(None, 'single message')
    value_with_multiple_messages = Value(123, ['some', 'messages'])
    extended_value = Value(value_with_multiple_messages, 'extra')
    extended_value.value      -->  123
    extended_value.messages   -->  ['some', 'messages', 'extra']

    """
    def __init__(self, value:T=None, messages:List[str]|str=None) -> None:
        self._values = []
        self._messages = []

        if isinstance(messages, str):   # if only one message is given
            messages = [messages]

        if messages is None:
            messages = []

        if isinstance(value, Value):
            if value.value is not None:
                self._values.insert(0, value.value)
            _messages = (value.messages + messages
                              if len(value.messages) > 0
                              else (messages if messages is not None else []))
            self._add_messages(_messages)
        else:
            if value is not None:
                if isinstance(value, list):
                    self._values = value
                else:
                    self._values.insert(0, value)
            _messages = messages if messages is not None else []
            self._add_messages(_messages)

    @property
    def value(self) -> T:
        if len(self._values) == 0:
            return None
        return self._values[0]

    @value.setter
    def value(self, _):
        raise PermissionError("The value property is read only")

    @property
    def values(self) -> List[T]:  # used if there are mulitiply stacked values
        return self._values

    @values.setter
    def values(self, _):
        raise PermissionError("The values property is read only")

    def stack(self, other) -> Value:
        if isinstance(other, Value):
            self._values = other.values + self._values
            self._add_messages(other.messages)
        else:
            self._values.insert(0, other)  # current value becomes second
        return self

    def __or__(self, other) -> Value:
        #  alias of bind method: "|"
        return self.stack(other)

    def pop(self) -> T:
        if len(self._values) > 0:
            return self._values.pop(0)   # second value becomes first
        else:
            return None

    def _add_messages(self, messages:List[str]):
        self._messages = list_remove_duplicates(self._messages + messages)

    @property
    def messages(self) -> List[str]:
        return self._messages

    @messages.setter
    def messages(self, _):
        raise PermissionError("The messages property is read only")

    @property
    def message(self) -> List[str]:
        return ' | '.join(self._messages) if len(self._messages) > 0 else ''

    @message.setter
    def message(self, _):
        raise PermissionError("The message property is read only")

    @property
    def items(self) -> Tuple[T, List[str]]:
        return self.value, self.messages

    @items.setter
    def items(self, _):
        raise PermissionError("The items property is read only")

    @property
    def items_all(self) -> Tuple[T, List[str]]:
        return self.values, self.messages

    @items_all.setter
    def items_all(self, _):
        raise PermissionError("The items_all property is read only")

    def prefix_messages(self, prefix:str='') -> Value:
        self._messages = [
                (str(prefix) + str(message) if message != '' else '')
                for message in self._messages]
        return self

    def suffix_messages(self, suffix:str='') -> Value:
        self._messages = [
                (str(message) + str(suffix) if message != '' else '')
                for message in self._messages]
        return self

    def bind(self, func: Callable[Value, Value]) -> Value:
        try:
            new_value_obj = func(self)
        except Exception as e:
            messages = self.messages + ['Error: {}'.format(
                            e.message if hasattr(e, 'message') else e)]
            return Value(self.values, messages) # only message, keep old values

        if new_value_obj.value is None: # only message, keep old values
            return Value(self.values,
                         self.messages + new_value_obj.messages)
        else:
            return Value(new_value_obj.values,
                         self.messages + new_value_obj.messages)

    def __rshift__(self, func: Callable[Value, Value]) -> Value:
        #  alias of bind method: ">>"
        return self.bind(func)

    __match_args__ = ("value",)

    def __match__(self, other: Value[T]) -> bool:
        return self.value == other.value

    def __repr__(self) -> str:
        fmt1 = 'idataframe.tools.Value({}, {})'
        fmt2 = 'idataframe.tools.Value({})'
        if len(self.values) > 1:
            if len(self.messages) > 1:
                return fmt1.format(self.values, self.messages)
            elif len(self.messages) == 0:
                return fmt2.format(self.values)
            else: # 1 message
                return fmt1.format(self.values, "'" + self.message + "'")
        else:
            if len(self.messages) > 1:
                if isinstance(self.value, str):
                    return fmt1.format("'" + self.value + "'", self.messages)
                else:
                    return fmt1.format(self.value, self.messages)
            elif len(self.messages) == 0:
                if isinstance(self.value, str):
                    return fmt2.format("'" + self.value + "'")
                else:
                    return fmt2.format(self.value)
            else: # 1 message
                if isinstance(self.value, str):
                    return fmt1.format("'" + self.value + "'", "'" + self.message + "'")
                else:
                    return fmt1.format(self.value, "'" + self.message + "'")

    def __str__(self) -> str:
        return str(self.value) if self.value is not None else str_na

    def __int__(self) -> int:
        return int(self.value) if self.value is not None else int_na

    def __float__(self) -> float:
        return float(self.value) if self.value is not None else float_na

    def __add__(self, other) -> Value:
        if isinstance(other, Value):
            return self.__class__(([(self.value + other.value
                 if self.value is not None and other.value is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.messages + other.messages)
        else:
            return self.__class__(([(self.value + other
                 if self.value is not None and other is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.messages)

    def __sub__(self, other) -> Value:
        if isinstance(other, Value):
            return self.__class__(([(self.value - other.value
                 if self.value is not None and other.value is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.messages + other.messages)
        else:
            return self.__class__(([(self.value - other
                 if self.value is not None and other is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.messages)

    def __mul__(self, other) -> Value:
        if isinstance(other, Value):
            return self.__class__(([(self.value * other.value
                 if self.value is not None and other.value is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.messages + other.messages)
        else:
            return self.__class__(([(self.value * other
                 if self.value is not None and other is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.messages)

    def __truediv__(self, other) -> Value:
        if isinstance(other, Value):
            return self.__class__(([(self.value / other.value
                 if self.value is not None and other.value is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.messages + other.messages)
        else:
            return self.__class__(([(self.value / other
                 if self.value is not None and other is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.messages)

    def __floordiv__(self, other) -> Value:
        if isinstance(other, Value):
            return self.__class__(([(self.value // other.value
                 if self.value is not None and other.value is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.messages + other.messages)
        else:
            return self.__class__(([(self.value // other
                 if self.value is not None and other is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.messages)

    def __pow__(self, other) -> Value:
        if isinstance(other, Value):
            return self.__class__(([(self.value ** other.value
                 if self.value is not None and other.value is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.messages + other.messages)
        else:
            return self.__class__(([(self.value ** other
                 if self.value is not None and other is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.messages)

    def __mod__(self, other) -> Value:
        if isinstance(other, Value):
            return self.__class__(([(self.value % other.value
                 if self.value is not None and other.value is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.messages + other.messages)
        else:
            return self.__class__(([(self.value % other
                 if self.value is not None and other is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.messages)

    def __divmod__(self, other) -> Value:
        if isinstance(other, Value):
            return self.__class__(([(divmod(self.value, other.value)
                 if self.value is not None and other.value is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.messages + other.messages)
        else:
            return self.__class__(([(divmod(self.value, other)
                 if self.value is not None and other is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.messages)

    def __neg__(self) -> Value:
        return self.__class__(([-self.value if self.value is not None else None]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.messages)

    def __pos__(self) -> Value:
        return self.__class__(([+self.value if self.value is not None else None]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.messages)

    def __abs__(self) -> Value:
        return self.__class__(([abs(self.value) if self.value is not None else None]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.messages)

    def __round__(self, ndigits=None) -> Value:
        return self.__class__(([round(self.value, ndigits) if self.value is not None else None]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.messages)


    # object.__matmul__(self, other)
    # object.__lshift__(self, other)
    # object.__rshift__(self, other)
    # object.__and__(self, other)
    # object.__xor__(self, other)
    # object.__or__(self, other)
    # object.__radd__(self, other)
    # object.__rsub__(self, other)
    # object.__rmul__(self, other)
    # object.__rmatmul__(self, other)
    # object.__rtruediv__(self, other)
    # object.__rfloordiv__(self, other)
    # object.__rmod__(self, other)
    # object.__rdivmod__(self, other)
    # object.__rpow__(self, other[, modulo])
    # object.__rlshift__(self, other)
    # object.__rrshift__(self, other)
    # object.__rand__(self, other)
    # object.__rxor__(self, other)
    # object.__ror__(self, other)
    # object.__iadd__(self, other)
    # object.__isub__(self, other)
    # object.__imul__(self, other)
    # object.__imatmul__(self, other)
    # object.__itruediv__(self, other)
    # object.__ifloordiv__(self, other)
    # object.__imod__(self, other)
    # object.__ipow__(self, other[, modulo])
    # object.__ilshift__(self, other)
    # object.__irshift__(self, other)
    # object.__iand__(self, other)
    # object.__ixor__(self, other)
    # object.__ior__(self, other)
    # object.__invert__(self)
    # object.__complex__(self)
    # object.__index__(self)
    # object.__trunc__(self)
    # object.__floor__(self)
    # object.__ceil__(self)


# -----------------------------------------------------------------------------


class ValueList():
    """
    List of Values objects.

    Of each Value object: only first value in stack will be used; rest of
    stack will be ignored.
    """
    def __init__(self, values:List[Value]=None):
        self._value_items = []
        if values is not None:
            for value in values:
                self.add(value)

    def add(self, value:Value) -> ValueList:
        if not isinstance(value, Value):
            raise TypeError("value_messages attribute must be a Value object (now value_messages type is {})".format(type(value)))

        self._value_items.append(value)
        return self

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
        return list_remove_duplicates(messages_list)

    @messages.setter
    def messages(self, _):
        raise PermissionError("The messages property is read only")
