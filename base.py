from typing import Any, List, Tuple

__all__ = ['ValueMessages', 'Value', 'ValueMessage', 'Messages', 'Message', 'VMList']


# -----------------------------------------------------------------------------


class ValueMessages():
    """
    Monad type containing a value and (optional) multiple text messages.
    """
    def __init__(self, value:Any=None, messages:List[str]=None):
        self._value = value
        self._messages = messages if messages is not None else []

    def prefix_messages(self, prefix:str='') -> 'ValueMessages':
        self._messages = [str(prefix) + str(message) for message in self._messages]
        return self

    def suffix_messages(self, suffix:str='') -> 'ValueMessages':
        self._messages = [str(message) + str(suffix) for message in self._messages]
        return self

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
        return self._messages[0] if len(self._messages) > 0 else ''

    @message.setter
    def message(self, _):
        raise PermissionError("The message property is read only")

    @property
    def items(self) -> Tuple[Any, List[str]]:
        return self.value, self.messages

    @items.setter
    def items(self, _):
        raise PermissionError("The items property is read only")


# -----------------------------------------------------------------------------


class Value(ValueMessages):
    def __init__(self, value:Any=None):
        super().__init__(value, None)


# -----------------------------------------------------------------------------


class ValueMessage(ValueMessages):
    def __init__(self, value:Any=None, message:str=None):
        super().__init__(value, [message])


# -----------------------------------------------------------------------------


class Messages(ValueMessages):
    def __init__(self, messages:List[str]=None):
        super().__init__(None, messages)


# -----------------------------------------------------------------------------


class Message(ValueMessages):
    def __init__(self, message:str=None):
        super().__init__(None, [message])


# -----------------------------------------------------------------------------


class VMList():
    """
    List of ValueMessages objects.
    """
    def __init__(self):
        self._value_messages_items = []

    def add(self, value_messages:ValueMessages) -> 'VMList':
        if not isinstance(value_messages, ValueMessages):
            raise TypeError("value_messages attribute must be a ValueMessages object (now value_messages type is {})".format(type(value_messages)))
        
        self._value_messages_items.append(value_messages)
        return 

    @property
    def items(self) -> List[ValueMessages]:
        return self._value_messages_items

    @items.setter
    def items(self, _):
        raise PermissionError("The items property is read only")

    @property
    def values(self) -> List[Any]:
        return [vm.value for vm in self._value_messages_items if vm.value is not None]

    @values.setter
    def values(self, _):
        raise PermissionError("The values property is read only")

    @property
    def messages(self) -> List[Any]:
        "Concaternate messages of objects."
        messages_list = []
        for vm in self._value_messages_items:
            messages_list = messages_list + vm.messages
        return messages_list

    @messages.setter
    def messages(self, _):
        raise PermissionError("The messages property is read only")
