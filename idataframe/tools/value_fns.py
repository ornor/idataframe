from idataframe.tools.value_obj import Value


def parse_int(v:Value) -> Value[int]:
    try:
        return Value(int(v.value))
    except Exception:
        return Value(None, 'Error parsing int: {}'.format(v.value))



def double(v:Value) -> Value[int|float]:
    return Value(2*v.value)


def concat(v:Value[str]) -> Value[str]:
    return Value(v.pop() + v.pop())
