from idataframe.base.Value import Value, value_fn
from idataframe.base.ValueList import ValueList

__all__ = ['Value', 'value_fn',
           'parse_int']


def parse_int(value: str) -> Value[int]:
    try:
        return Value(int(value))
    except ValueError:
        return Value(None)