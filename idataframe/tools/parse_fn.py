from idataframe.tools.value_obj import Value

__all__ = ['parse_int']


def parse_int(value: str) -> Value[int]:
    try:
        return Value(int(value))
    except ValueError:
        return Value(None)

