from __future__ import annotations
from typing import Any, Generic, TypeVar, Callable, List, Tuple

__all__ = []  # will be extended inside this file


# -----------------------------------------------------------------------------


T = TypeVar("T")
U = TypeVar("U")


__all__.append('Value')
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
        if isinstance(messages, str):   # if only one message is given
            messages = [messages]

        if isinstance(value, Value):
            self._value = value._value
            self._messages = value.messages + messages if len(value.messages) > 0 else (messages if messages is not None else [])
        else:
            self._value = value
            self._messages = messages if messages is not None else []

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, _):
        raise PermissionError("The value property is read only")

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
        self._messages = [str(prefix) + str(message) for message in self._messages]
        return self

    def suffix_messages(self, suffix:str='') -> Value:
        self._messages = [str(message) + str(suffix) for message in self._messages]
        return self

    def bind(self, func: Callable[[T], Value[U]]) -> Value[T] | Value[U]:
        return self if self.value is None else func(self.value)

    __match_args__ = ("value",)

    def __match__(self, other: Value[T]) -> bool:
        return self.value == other.value

# -----------------------------------------------------------------------------


__all__.append('value_fn')
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
        except Exception:
            return Value(None, 'ERROR')   #TODO  name inside error

    return wrapper

# -----------------------------------------------------------------------------


__all__.append('ValueList')
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


# -----------------------------------------------------------------------------

__all__.append('parse_int')
def parse_int(value: str) -> Value[int]:
    try:
        return Value(int(value))
    except ValueError:
        return Value(None)