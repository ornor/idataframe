import re
from functools import reduce
import operator

from idataframe.tools.value_obj import is_na, na, Value, Message

# -----------------------------------------------------------------------------

def parse_int(v:Value) -> Value[int]:
    val, stack = v.unstack(1)
    if is_na(val):
        return Value(na) ^ stack
    try:
        return Value(int(val)) ^ stack
    except Exception:
        return Message('Error parsing int: {}'.format(val)) ^ stack

def parse_float(v:Value) -> Value[float]:
    val, stack = v.unstack(1)
    if is_na(val):
        return Value(na) ^ stack
    try:
        return Value(float(val)) ^ stack
    except Exception:
        return Message('Error parsing float: {}'.format(val)) ^ stack

def parse_str(v:Value) -> Value[str]:
    val, stack = v.unstack(1)
    if is_na(val):
        return Value(na) ^ stack
    try:
        return Value(str(val)) ^ stack
    except Exception:
        return Message('Error parsing str: {}'.format(val)) ^ stack

# -----------------------------------------------------------------------------

def map_fn(map_fn):
    def fn(v:Value) -> Value:
        val, stack = v.unstack(1)
        try:
            return Value(map_fn(val)) ^ stack
        except Exception:
            return Message('Error mapping: {}'.format(val)) ^ stack
    return fn

def replace_na(replace_value):
    def fn(v:Value) -> Value:
        val, stack = v.unstack(1)
        return Value(replace_value if is_na(val) else val) ^ stack

    return fn

# -----------------------------------------------------------------------------

def stack_sum(v:Value[float|int]) -> Value[float|int]:
    return Value(reduce(operator.add, v.values, 0))

def stack_product(v:Value[float|int]) -> Value[float|int]:
    return Value(reduce(operator.mul, v.values, 1))

def stack_concat(v:Value[str]) -> Value[str]:
    return Value(reduce(operator.concat, v.values, ''))

def stack_reverse(v:Value) -> Value:
    return Value(list(reversed(v.values)))

def stack_map(map_fn):
    def fn(v:Value) -> Value:
        return Value(list(map(map_fn, v.values)))
    return fn

def stack_replace_na(replace_value):
    def fn(v:Value) -> Value:
        return Value([(replace_value if is_na(x) else x) for x in v.values])
    return fn

# -----------------------------------------------------------------------------

def match(regexp:str):
    keys = [part.split('>')[0] for part in regexp.split('(?P<')[1:]]
    def fn(v:Value[str]) -> Value[str]:
        text, stack = v.unstack(1)
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
            return Value(text, {
                    'match_found': None,
                    'fields': fields
                }) ^ stack
    return fn

def f_str(format_str:str):
    def fn(v:Value[str]) -> Value[str]:
        text, stack = v.unstack(1)
        if 'fields' in v and 'match_found' in v: # found something earlier
            del v['match_found']
            return Value(format_str.format(**v['fields'])) ^ stack
        else:
            return Value(text) ^ stack
    return fn
