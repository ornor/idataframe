import abc

__all__ = ['BaseField']


class BaseField(abc.ABC):
    def __init__(self, post_parse_fn=None):
        self.post_parse_fn = post_parse_fn if callable(post_parse_fn) else lambda value: value

    @property
    @abc.abstractmethod
    def series_type(self):
        pass

    @abc.abstractmethod
    def str_to_type_fn(self, value:str):
        pass