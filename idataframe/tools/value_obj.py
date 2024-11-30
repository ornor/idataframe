from __future__ import annotations
from typing import Any, Generic, TypeVar, Callable, List, Tuple

from idataframe.tools import list_remove_duplicates

__all__ = ['Value', 'value_fn', 'ValueList']


# -----------------------------------------------------------------------------


T = TypeVar("T")
U = TypeVar("U")


class Value(Generic[T]):
    """
    Monad type containing a value and (optional) multiple text messages.

    Based on: https://github.com/ArjanCodes/examples/blob/main/2023/monad/maybe_railroad_v2.py


    only_value = Value(123)
    only_message = Value(None, 'single message')
    value_with_multiple_messages = Value(123, ['some', 'messages'])
    extended_value = Value(value_with_multiple_messages, 'extra')
    extended_value.value      -->  123
    extended_value.messages   -->  ['some', 'messages', 'extra']

    """
    def __init__(self, value:T=None, messages:List[str]|str=None) -> None:
        self._value = None
        self._messages = []

        if isinstance(messages, str):   # if only one message is given
            messages = [messages]

        if isinstance(value, Value):
            self._value = value._value
            _messages = (value.messages + messages
                              if len(value.messages) > 0
                              else (messages if messages is not None else []))
            self._add_messages(_messages)
        else:
            self._value = value
            _messages = messages if messages is not None else []
            self._add_messages(_messages)

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, _):
        raise PermissionError("The value property is read only")

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
    def items(self) -> Tuple[Any, List[str]]:
        return self.value, self.messages

    @items.setter
    def items(self, _):
        raise PermissionError("The items property is read only")

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

    def bind(self, func: Callable[[T], Value[U]]) -> Value[T] | Value[U]:
        return self if self.value is None else func(self.value)

    __match_args__ = ("value",)

    def __match__(self, other: Value[T]) -> bool:
        return self.value == other.value

    def __repr__(self) -> str:
        return 'idataframe.tools.Value{}'.format(str(self.items))

    def __str__(self) -> str:
        return str(self.value)

    def __int__(self) -> int:
        return int(self.value)

    def __float__(self) -> float:
        return float(self.value)

    def __add__(self, other) -> Value:
        if isinstance(other, Value):
            return self.__class__(self.value + other.value,
                              self.messages + other.messages)
        else:
            return self.__class__(self.value + other, self.messages)

    def __sub__(self, other) -> Value:
        if isinstance(other, Value):
            return self.__class__(self.value - other.value,
                              self.messages + other.messages)
        else:
            return self.__class__(self.value - other, self.messages)

    def __mul__(self, other) -> Value:
        if isinstance(other, Value):
            return self.__class__(self.value * other.value,
                              self.messages + other.messages)
        else:
            return self.__class__(self.value * other, self.messages)

    def __truediv__(self, other) -> Value:
        if isinstance(other, Value):
            return self.__class__(self.value / other.value,
                              self.messages + other.messages)
        else:
            return self.__class__(self.value / other, self.messages)

    def __floordiv__(self, other) -> Value:
        if isinstance(other, Value):
            return self.__class__(self.value // other.value,
                              self.messages + other.messages)
        else:
            return self.__class__(self.value // other, self.messages)

    def __pow__(self, other) -> Value:
        if isinstance(other, Value):
            return self.__class__(self.value ** other.value,
                              self.messages + other.messages)
        else:
            return self.__class__(self.value ** other, self.messages)

    def __mod__(self, other) -> Value:
        if isinstance(other, Value):
            return self.__class__(self.value % other.value,
                              self.messages + other.messages)
        else:
            return self.__class__(self.value % other, self.messages)


    def __divmod__(self, other) -> Value:
        if isinstance(other, Value):
            return self.__class__(divmod(self.value, other.value),
                              self.messages + other.messages)
        else:
            return self.__class__(divmod(self.value, other), self.messages)

    def __neg__(self) -> Value:
        return self.__class__(-self.value, self.messages)

    def __pos__(self) -> Value:
        return self.__class__(+self.value, self.messages)

    def __abs__(self) -> Value:
        return self.__class__(abs(self.value), self.messages)


      # object.__invert__(self)
      # object.__complex__(self)
      # object.__index__(self)
      # object.__round__(self[, ndigits])
      # object.__trunc__(self)
      # object.__floor__(self)
      # object.__ceil__(self)


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


# -----------------------------------------------------------------------------


def value_fn(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to create Value binding from function, including error handling.


    @value_fn
    def double(value: int) -> int:
        return 2 * value

    Value(123).bind(double).value  -->  246
    """
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return Value(func(*args, **kwargs))
        except Exception as e:
            return Value(None, 'Error Value init: {}'.format(
                    e.message if hasattr(e, 'message') else e))

    return wrapper


# -----------------------------------------------------------------------------


class ValueList():
    """
    List of Values objects.
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
