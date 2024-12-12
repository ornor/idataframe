import re

from idataframe.tools.value_obj import Value


def parse_int(v:Value) -> Value[int]:
    val, stack = v.pop(1)
    try:
        return Value(int(val)) ^ stack
    except Exception:
        return Value(None, 'Error parsing int: {}'.format(val)) ^ stack

def parse_float(v:Value) -> Value[float]:
    val, stack = v.pop(1)
    try:
        return Value(float(val)) ^ stack
    except Exception:
        return Value(None, 'Error parsing float: {}'.format(val)) ^ stack

def parse_str(v:Value) -> Value[str]:
    val, stack = v.pop(1)
    try:
        return Value(str(val)) ^ stack
    except Exception:
        return Value(None, 'Error parsing str: {}'.format(val)) ^ stack


def match(regexp:str):
    keys = [part.split('>')[0] for part in regexp.split('(?P<')[1:]]
    def fn(v:Value[str]) -> Value[str]:
        text, stack = v.pop(1)
        if isinstance(text, dict): # already found something earlier
            return Value(text) ^ stack
        fields = {}
        m = re.search(regexp, text)
        if m is None:
            return Value(text) ^ stack
        else:
            for key in keys:
                try:
                    fields[key] = m.group(key)
                except:
                    fields[key] = ''
            return Value(fields) ^ stack
    return fn

def form(format_str:str):
    def fn(v:Value[str]) -> Value[str]:
        data, stack = v.pop(1)
        if isinstance(data, dict): # found something earlier
            return Value(format_str.format(**data)) ^ stack
        else:
            return Value(data) ^ stack
    return fn



# def double(v:Value) -> Value[int|float]:
#     v1, stack = v.pop(1)
#     return Value(2* v1) ^ stack


# def concat(v:Value[str]) -> Value[str]:
#     v1, v2, stack = v.pop(2)
#     return Value(v1 + v2) ^ stack
