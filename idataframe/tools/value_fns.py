import re
from functools import reduce
import operator

from idataframe.tools.value_obj import is_na, na, Value, Message

__all__ = [
            'print_', 'debug',
            'else_', 'end_if',
            'parse_int', 'parse_float', 'parse_str',
            'map_fn', 'replace_na',
            'stack_sum', 'stack_product', 'stack_concat', 'stack_reverse',
                'stack_reverse',
            'if_str_match', 'elif_str_match', 'format_str_by_groups',
          ]

def print_(txt:str):
    def fn(v:Value):
        print(txt)
        return v
    return fn

def debug():
    count = 0
    remove_left = repr(Value('dummy')).split('Value')[0]
    def fn(v:Value):
        nonlocal count
        print('[#{:>3}] {}'.format(count, repr(v).lstrip(remove_left)))
        count += 1
        return v
    return fn

# -----------------------------------------------------------------------------

_META_IF = 'if'
_META_IF_FALSE = 0
_META_IF_TRUE = 1
_META_IF_PERMANENT_FALSE = 2

def _set_if(v:Value, if_value:int) -> Value:
    """
    Sets _META_IF as a new level.
    v[_META_IF] contains list containing if-values (bools) of each nested level
    """
    if _META_IF not in v:
        v[_META_IF] = [if_value]
    else:
        if len(v[_META_IF]) > 0: # create extra nested level
            v[_META_IF].insert(0, if_value)
        else:
            v[_META_IF].append(if_value)
    return v

def _replace_if(v:Value, if_value:int) -> Value:
    """
    Replace _META_IF in current level.
    v[_META_IF] contains list containing if-values (bools) of each nested level
    """
    if _META_IF not in v or len(v[_META_IF]) < 1:
        return Message('Error: no if-statement found.') ^ v.values
    else:
        v[_META_IF][0] = if_value
    return v

def _get_if(v:Value) -> int:
    """
    Gets _META_IF value or None is no if-level is set.
    """
    if _META_IF not in v or len(v[_META_IF]) < 1:
        return None
    else:
        return v[_META_IF][0]

def _check_break_fn(v: Value) -> bool:
    if_value = _get_if(v)
    return if_value == _META_IF_FALSE or if_value == _META_IF_PERMANENT_FALSE

def else_(v:Value) -> Value:
    if _META_IF not in v or len(v[_META_IF]) < 1:
        return Message('Error: no if-statement found.') ^ v.values
    else:
        if_value = v[_META_IF][0]
        if if_value == _META_IF_TRUE:
            v[_META_IF][0] = _META_IF_FALSE
        elif if_value == _META_IF_FALSE:
            v[_META_IF][0] = _META_IF_TRUE
        elif if_value == _META_IF_PERMANENT_FALSE:
            pass # leave value permanent false
        return v

def end_if(v:Value) -> Value:
    """
    Remove _META_IF value. End current if level.
    """
    if _META_IF not in v or len(v[_META_IF]) < 1:
        return Message('Error: no if-statement found.') ^ v.values
    else:
        if len(v[_META_IF]) > 1:
            _ = v[_META_IF].pop(0)
        else:
            del v[_META_IF]
    return v

# -----------------------------------------------------------------------------

def parse_int(v:Value) -> Value[int]:
    if _check_break_fn(v): return v
    val, stack = v.unstack(1)
    if is_na(val):
        return Value(na) ^ stack
    try:
        return Value(int(val)) ^ stack
    except Exception:
        return Message('Error parsing int: {}'.format(val)) ^ stack

def parse_float(v:Value) -> Value[float]:
    if _check_break_fn(v): return v
    val, stack = v.unstack(1)
    if is_na(val):
        return Value(na) ^ stack
    try:
        return Value(float(val)) ^ stack
    except Exception:
        return Message('Error parsing float: {}'.format(val)) ^ stack

def parse_str(v:Value) -> Value[str]:
    if _check_break_fn(v): return v
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
        if _check_break_fn(v): return v
        val, stack = v.unstack(1)
        try:
            return Value(map_fn(val)) ^ stack
        except Exception:
            return Message('Error mapping: {}'.format(val)) ^ stack
    return fn

def replace_na(replace_value):
    def fn(v:Value) -> Value:
        if _check_break_fn(v): return v
        val, stack = v.unstack(1)
        return Value(replace_value if is_na(val) else val) ^ stack

    return fn

# -----------------------------------------------------------------------------

def stack_sum(v:Value[float|int]) -> Value[float|int]:
    if _check_break_fn(v): return v
    return Value(reduce(operator.add, v.values, 0))

def stack_product(v:Value[float|int]) -> Value[float|int]:
    if _check_break_fn(v): return v
    return Value(reduce(operator.mul, v.values, 1))

def stack_concat(v:Value[str]) -> Value[str]:
    if _check_break_fn(v): return v
    return Value(reduce(operator.concat, v.values, ''))

def stack_reverse(v:Value) -> Value:
    if _check_break_fn(v): return v
    return Value(list(reversed(v.values)))

def stack_map(map_fn):
    def fn(v:Value) -> Value:
        if _check_break_fn(v): return v
        return Value(list(map(map_fn, v.values)))
    return fn

def stack_replace_na(replace_value):
    def fn(v:Value) -> Value:
        if _check_break_fn(v): return v
        return Value([(replace_value if is_na(x) else x) for x in v.values])
    return fn

# -----------------------------------------------------------------------------

_META_STR_MATCH_GROUPS = 'groups'

def if_str_match(regexp:str, else_if:bool=False):
    keys = [part.split('>')[0] for part in regexp.split('(?P<')[1:]]
    def fn(v:Value[str]) -> Value[str]:
        v = ((_replace_if(v, _META_IF_TRUE)
             if _get_if(v) == _META_IF_FALSE
             else (_replace_if(v, _META_IF_PERMANENT_FALSE)
                   if _get_if(v) == _META_IF_TRUE else v))
            if else_if else v)
        if _check_break_fn(v): return v
        text, stack = v.unstack(1)
        fields = {}
        m = re.search(regexp, text)
        if m is None:  # no results
            return (_replace_if(v, _META_IF_FALSE) if else_if
                    else _set_if(v, _META_IF_FALSE))
        else:
            for key in keys:
                try:
                    fields[key] = m.group(key)
                except:
                    fields[key] = ''
            v[_META_STR_MATCH_GROUPS] = fields
            return (_replace_if(v, _META_IF_TRUE) if else_if
                    else _set_if(v, _META_IF_TRUE))
    return fn

def elif_str_match(regexp:str, else_if=True):
    return if_str_match(regexp, else_if)

def format_str_by_groups(fmt_str:str):
    def fn(v:Value[str]) -> Value[str]:
        if _check_break_fn(v): return v
        text, stack = v.unstack(1)
        if _META_STR_MATCH_GROUPS in v:
            return Value(fmt_str.format(**v[_META_STR_MATCH_GROUPS])) ^ stack
        else:
            return Value(text) ^ stack
    return fn
