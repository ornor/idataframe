from __future__ import annotations
from typing import Generic, TypeVar, Callable, List

import numpy as np
import pandas as pd

from idataframe.tools import list_remove_duplicates

__all__ = ['na', 'is_na',
           'Value', 'Message']


# -----------------------------------------------------------------------------


na = pd.NA

def is_na(value:str|int|float|Value) -> bool:
    if value is None or value is na:
        return True
    elif isinstance(value, str):
        return value == ''
    elif isinstance(value, int):
        return pd.isna(value)
    elif isinstance(value, float):
        return np.isnan(value)
    elif isinstance(value, Value):
        return is_na(value.value)
    else:
        try:
            return pd.isna(value)
        except:
            try:
                return np.isnan(value)
            except:
                return False


# -----------------------------------------------------------------------------


T = TypeVar("T")
U = TypeVar("U")


class Value(Generic[T]):
    """
    Kind of monad type containing a value, metadata and (optional) multiple
    text messages.

    Based on: https://github.com/ArjanCodes/examples/blob/main/2023/monad/maybe_railroad_v2.py

    """
    def __init__(self, value:T=None,
                       meta:dict=None,
                       messages:List[str]|str=None) -> None:
        self._values = []
        self._meta = {}
        self._messages = []

        if isinstance(messages, str):   # if only one message is given
            messages = [messages]

        if messages is None:
            messages = []

        if isinstance(value, Value):
            if value.value is not None:
                self._values.append(value.value)
            _messages = (value.messages + messages
                              if len(value.messages) > 0
                              else (messages if messages is not None else []))
            self._messages = list_remove_duplicates(self._messages + _messages)
            if meta is None:
                self._meta = value.meta
            else:
                self._meta = {**value.meta, **meta}
        else:
            if value is not None:
                if isinstance(value, list):
                    self._values = value
                else:
                    self._values.append(value)
            _messages = messages if messages is not None else []
            self._messages = list_remove_duplicates(self._messages + _messages)
            if meta is not None:
                self._meta = meta

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
    def meta(self) -> dict:  #TODO test
        return self._meta

    @meta.setter
    def meta(self, _):
        raise PermissionError("The meta property is read only")

    def __getitem__(self, key):   #TODO test
        if key not in self._meta:
            return None
        else:
            return self._meta[key]

    def __setitem__(self, key, value):   #TODO test
        self._meta[key] = value

    def __delitem__(self, key):   #TODO test
        del self._meta[key]

    def __contains__(self, key):   #TODO test
        return key in self.meta

    def stack(self, other) -> Value:
        return_obj = self.copy()
        if isinstance(other, Value):
            return_obj._values = return_obj._values + other.values
            return_obj._meta = {**return_obj._meta, **other.meta}
            return_obj._messages = list_remove_duplicates(
                                        return_obj._messages + other.messages)
        elif isinstance(other, list):
            return_obj._values = return_obj._values + other
        else:
            return_obj._values.append(other)
        return return_obj

    def __xor__(self, other) -> Value:
        #  alias of stack method: "^"
        return self.stack(other)

    def unstack(self, count:int) -> tuple:
        if len(self.values) < count:
            count_missing = count - len(self.values)
            new_stack = []
            none_stack = self.values + [
                None for _ in range(count_missing)] + [new_stack]
            return tuple(none_stack)
        return_values = self.values[:count]
        new_stack = self.values[count:]
        return tuple(return_values + [new_stack])

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

    def copy(self):
        return self.__class__(self.values, self.meta, self.messages)

    def bind(self, func: Callable[Value, Value]) -> Value:
        try:
            new_value_obj = func(self)
        except Exception as e:
            messages = self.messages + ['Error: {}'.format(
                            e.message if hasattr(e, 'message') else e)]
            # only message, keep old values
            return Value(self.values, self.meta, messages)

        if new_value_obj.value is None: # only message, keep old values
            return Value(self.values,
                         {**self.meta, **new_value_obj.meta},
                         self.messages + new_value_obj.messages)
        else:
            return Value(new_value_obj.values,
                         {**self.meta, **new_value_obj.meta},
                         self.messages + new_value_obj.messages)

    def __or__(self, func: Callable[Value, Value]) -> Value:
        #  alias of bind method: "|"
        return self.bind(func)

    __match_args__ = ("value",)

    def __match__(self, other: Value[T]) -> bool:
        return self.value == other.value

    def __repr__(self) -> str:
        fmt1 = 'idataframe.tools.Value({})'
        fmt2 = 'idataframe.tools.Value({}, {})'
        fmt3 = 'idataframe.tools.Value({}, {}, {})'
        if len(self.values) > 1:
            if len(self.messages) > 1:
                if len(self.meta) > 0:
                    return fmt3.format(self.values, self.meta, self.messages)
                else:
                    return fmt3.format(self.values, None, self.messages)
            elif len(self.messages) == 0:
                if len(self.meta) > 0:
                    return fmt2.format(self.values, self.meta)
                else:
                    return fmt1.format(self.values)
            else: # 1 message
                if len(self.meta) > 0:
                    return fmt3.format(self.values, self.meta,
                                           "'" + self.message + "'")
                else:
                    return fmt3.format(self.values, None,
                                           "'" + self.message + "'")
        else:
            if len(self.messages) > 1:
                if isinstance(self.value, str):
                    if len(self.meta) > 0:
                        return fmt3.format("'" + self.value + "'",
                                               self.meta, self.messages)
                    else:
                        return fmt3.format("'" + self.value + "'",
                                               None, self.messages)
                else:
                    if len(self.meta) > 0:
                        return fmt3.format(self.value, self.meta,
                                                           self.messages)
                    else:
                        return fmt3.format(self.value, None, self.messages)
            elif len(self.messages) == 0:
                if isinstance(self.value, str):
                    if len(self.meta) > 0:
                        return fmt2.format("'" + self.value + "'",
                                                              self.meta)
                    else:
                        return fmt1.format("'" + self.value + "'")
                else:
                    if len(self.meta) > 0:
                        return fmt2.format(self.value, self.meta)
                    else:
                        return fmt1.format(self.value)
            else: # 1 message
                if isinstance(self.value, str):
                    if len(self.meta) > 0:
                        return fmt3.format("'" + self.value + "'", self.meta,
                                           "'" + self.message + "'")
                    else:
                        return fmt3.format("'" + self.value + "'", None,
                                           "'" + self.message + "'")
                else:
                    if len(self.meta) > 0:
                        return fmt3.format(self.value, self.meta,
                                           "'" + self.message + "'")
                    else:
                        return fmt3.format(self.value, None,
                                           "'" + self.message + "'")

    def __str__(self) -> str:
        return str(self.value)

    def __int__(self) -> int:
        raise PermissionError("Blocked 'int' method. Use 'idataframe.tools.parse_int' method or 'self.value' attribute instead.")

    def __float__(self) -> float:
        raise PermissionError("Blocked 'float' method. Use 'idataframe.tools.parse_float' method or 'self.value' attribute instead.")

    def __add__(self, other) -> Value:
        if isinstance(other, Value):
            return self.__class__(([(self.value + other.value
                 if self.value is not None and other.value is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              {**self.meta, **other.meta},
                              self.messages + other.messages)
        else:
            return self.__class__(([(self.value + other
                 if self.value is not None and other is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.meta, self.messages)

    def __sub__(self, other) -> Value:
        if isinstance(other, Value):
            return self.__class__(([(self.value - other.value
                 if self.value is not None and other.value is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              {**self.meta, **other.meta},
                              self.messages + other.messages)
        else:
            return self.__class__(([(self.value - other
                 if self.value is not None and other is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.meta, self.messages)

    def __mul__(self, other) -> Value:
        if isinstance(other, Value):
            return self.__class__(([(self.value * other.value
                 if self.value is not None and other.value is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              {**self.meta, **other.meta},
                              self.messages + other.messages)
        else:
            return self.__class__(([(self.value * other
                 if self.value is not None and other is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.meta, self.messages)

    def __truediv__(self, other) -> Value:
        if isinstance(other, Value):
            return self.__class__(([(self.value / other.value
                 if self.value is not None and other.value is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              {**self.meta, **other.meta},
                              self.messages + other.messages)
        else:
            return self.__class__(([(self.value / other
                 if self.value is not None and other is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.meta, self.messages)

    def __floordiv__(self, other) -> Value:
        if isinstance(other, Value):
            return self.__class__(([(self.value // other.value
                 if self.value is not None and other.value is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              {**self.meta, **other.meta},
                              self.messages + other.messages)
        else:
            return self.__class__(([(self.value // other
                 if self.value is not None and other is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.meta, self.messages)

    def __pow__(self, other) -> Value:
        if isinstance(other, Value):
            return self.__class__(([(self.value ** other.value
                 if self.value is not None and other.value is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              {**self.meta, **other.meta},
                              self.messages + other.messages)
        else:
            return self.__class__(([(self.value ** other
                 if self.value is not None and other is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.meta, self.messages)

    def __mod__(self, other) -> Value:
        if isinstance(other, Value):
            return self.__class__(([(self.value % other.value
                 if self.value is not None and other.value is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              {**self.meta, **other.meta},
                              self.messages + other.messages)
        else:
            return self.__class__(([(self.value % other
                 if self.value is not None and other is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.meta, self.messages)

    def __divmod__(self, other) -> Value:
        if isinstance(other, Value):
            return self.__class__(([(divmod(self.value, other.value)
                 if self.value is not None and other.value is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              {**self.meta, **other.meta},
                              self.messages + other.messages)
        else:
            return self.__class__(([(divmod(self.value, other)
                 if self.value is not None and other is not None
                 else None)]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.meta, self.messages)

    def __neg__(self) -> Value:
        return self.__class__(([-self.value if self.value is not None else None]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.meta, self.messages)

    def __pos__(self) -> Value:
        return self.__class__(([+self.value if self.value is not None else None]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.meta, self.messages)

    def __abs__(self) -> Value:
        return self.__class__(([abs(self.value) if self.value is not None else None]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.meta, self.messages)

    def __round__(self, ndigits=None) -> Value:
        return self.__class__(([round(self.value, ndigits) if self.value is not None else None]
                    + (self.values[1:] if len(self.values) > 1 else [])),
                              self.meta, self.messages)


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


class Message(Value):
    def __init__(self, messages:List[str]|str=None) -> None:
        super().__init__(None, None, messages)
        self.__class__ = Value
