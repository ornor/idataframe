from idataframe.fields.BaseField import BaseField

__all__ = ['FloatField']


class FloatField(BaseField):
    series_type = 'Float64'    # Pandas Series type; don't use `float` as type because then it can't contain NaN values

    def __init__(self, parse_fn=None):
        super().__init__(parse_fn)

    def str_to_type_fn(self, value):
        return float(value)
