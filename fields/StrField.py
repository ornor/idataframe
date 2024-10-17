from idataframe.fields.BaseField import BaseField

__all__ = ['StrField']


class StrField(BaseField):
    series_type = 'str'   # Pandas Series type

    def __init__(self, parse_fn=None):
        super().__init__(parse_fn)

    def str_to_type_fn(self, value):
        return value