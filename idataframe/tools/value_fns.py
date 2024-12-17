import re
from functools import reduce, wraps
from typing import Callable, Any, Tuple
import operator
import textwrap

from idataframe.tools.value_obj import is_na, na, Value, Message

__all__ = [
            'debug',
            'else_', 'end_if',
            'change', 'log',
            'parse_int', 'parse_float', 'parse_str',
            'map_fn', 'replace_na',
            'stack_sum', 'stack_product', 'stack_concat', 'stack_reverse',
                'stack_map_fn', 'stack_replace_na',
            'if_str_match', 'elif_str_match', 'format_str_by_groups',
            'if_value_greater_than', 'elif_value_greater_than',
            'if_value_greater_equal_than', 'elif_value_greater_equal_than',
            'if_value_less_than', 'elif_value_less_than',
            'if_value_less_equal_than', 'elif_value_less_equal_than',
            'if_value_equal_to', 'elif_value_equal_to',
          ]

_META_DEBUG = 'debug'

def debug(set_on:bool=True):
    def fn(v:Value[Any]):
        if set_on:
            v[_META_DEBUG] = True
        else:
            if _META_DEBUG in v:
                del v[_META_DEBUG]
        return v
    return fn
    # count = 0
    # remove_left = repr(Value('dummy')).split('Value')[0]
    # def fn(v:Value):
    #     nonlocal count
    #     print('[#{:>3}] {}'.format(count, repr(v).lstrip(remove_left)))
    #     count += 1
    #     return v
    # return fn

# -----------------------------------------------------------------------------

_META_IF = 'if'
_META_IF_FALSE           = 0
_META_IF_TRUE            = 1
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

def _check_break_fn(v:Value[Any]) -> bool:
    """
    Helper function to check if function has to be aborted because of 'if'.

    Parameters
    ----------
    v : Value[Any]
        Input Value object.

    Returns
    -------
    bool
        If True: function has to be aborted.
        If False: can continue using function.

    Example
    -------
    # use line below as first line in function:
    if _check_break_fn(v): return v
    """
    if_value = _get_if(v)
    return if_value == _META_IF_FALSE or if_value == _META_IF_PERMANENT_FALSE

def _value_fn(fn_title:str,
              manual_break:bool=False,
              pre_fn:Callable[Value[Any], Value[Any]]=None,
              post_fn:Callable[Value[Any], Value[Any]]=None):
    repr_left = repr(Value('dummy')).split('Value')[0]
    def decorator(fn):
        @wraps(fn)
        def wrapper(v:Value[Any]) -> Value[Any]:
            if pre_fn is not None:
                v = pre_fn(v)
            # ----------------------
            if _check_break_fn(v) and not manual_break:
                return_value = v
            else:
                return_value = fn(v)
                if _META_DEBUG in v:
                    if_value = _get_if(v)
                    if if_value == True:
                        print('- {}\n    {}'.format(
                            fn_title,
                            '\n    '.join(textwrap.wrap(repr(v).lstrip(repr_left),
                                          width=50))
                        ))
                    else:
                        print('- {}'.format(fn_title))
            # ----------------------
            if post_fn is not None:
                v = post_fn(v)
            return return_value
        return wrapper
    return decorator

def _if_value_valid_fn(fn_title:str,
                       test_valid_fn:Callable[Value[Any], Tuple[bool, Any]],
                       if_true_fn:Callable[[Value[Any], Any], Value[Any]],
                       if_false_fn:Callable[[Value[Any], Any], Value[Any]],
                       else_if: bool
                       ) -> Callable[Value[Any], Value[Any]]:
    """
    Helper function to compose 'if' (and 'elif') functions.

    Parameters
    ----------
    test_valid_fn : Callable[Value[Any], Tuple[bool, Any]]
        Tests Value object and returns outcome and optional extra data.
    if_true_fn : Callable[[Value[Any], Any], Value[Any]]
        Calls when test is True, using Value object and optional extra test
        data.
    if_false_fn : Callable[[Value[Any], Any], Value[Any]]
        Calls when test is False, using Value object and optional extra test
        data.
    else_if : bool
        When True, function will act like an 'elif' function, instead of 'if'.

    Returns
    -------
    Callable[Value[Any], Value[Any]]
        Wrapping function usable as Value function.

    """
    @_value_fn(fn_title, manual_break=True)
    def fn(v: Value[Any]) -> Value[Any]:
        v = ((_replace_if(v, _META_IF_TRUE)
             if _get_if(v) == _META_IF_FALSE
             else (_replace_if(v, _META_IF_PERMANENT_FALSE)
                   if _get_if(v) == _META_IF_TRUE else v))
            if else_if else v)
        if _check_break_fn(v): return v
        valid, test_data = test_valid_fn(v)
        if valid:
            v = if_true_fn(v, test_data)
            return (_replace_if(v, _META_IF_TRUE) if else_if
                    else _set_if(v, _META_IF_TRUE))
        else:
            v = if_false_fn(v, test_data)
            return (_replace_if(v, _META_IF_FALSE) if else_if
                    else _set_if(v, _META_IF_FALSE))
    return fn

def else_():
    @_value_fn('else_', manual_break=True)
    def fn(v:Value[Any]) -> Value[Any]:
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
    return fn

def end_if():
    """
    Removes _META_IF value. End current 'if' level.

    Parameters
    ----------
    v : Value[Any]
        Input Value object.

    Returns
    -------
    Value[Any]
        Unchanged output Value object (except 'if' level).
    """
    @_value_fn('end_if', manual_break=True)
    def fn(v:Value[Any]) -> Value[Any]:
        if _META_IF not in v or len(v[_META_IF]) < 1:
            return Message('Error: no if-statement found.') ^ v.values
        else:
            if len(v[_META_IF]) > 1:
                _ = v[_META_IF].pop(0)
            else:
                del v[_META_IF]
        return v
    return fn

# -----------------------------------------------------------------------------

def log(txt:str=None):
    @_value_fn('log(' + txt + ')')
    def fn(v:Value[Any]) -> Value[Any]:
        if txt is None:
            print(v)
        else:
            print(txt)
        return v
    return fn

def change(new_value):
    @_value_fn('change(' + new_value + ')')
    def fn(v:Value[Any]) -> Value[Any]:
        _, stack = v.unstack(1)
        return Value(new_value) ^ stack
    return fn

# -----------------------------------------------------------------------------

def parse_int():
    @_value_fn('parse_int')
    def fn(v:Value[Any]) -> Value[int]:
        val, stack = v.unstack(1)
        if is_na(val):
            return Value(na) ^ stack
        try:
            return Value(int(val)) ^ stack
        except Exception:
            return Message('Error parsing int: {}'.format(val)) ^ stack
    return fn

def parse_float():
    @_value_fn('parse_float')
    def fn(v:Value[Any]) -> Value[float]:
        val, stack = v.unstack(1)
        if is_na(val):
            return Value(na) ^ stack
        try:
            return Value(float(val)) ^ stack
        except Exception:
            return Message('Error parsing float: {}'.format(val)) ^ stack
    return fn

def parse_str():
    @_value_fn('parse_str')
    def fn(v:Value[Any]) -> Value[str]:
        val, stack = v.unstack(1)
        if is_na(val):
            return Value(na) ^ stack
        try:
            return Value(str(val)) ^ stack
        except Exception:
            return Message('Error parsing str: {}'.format(val)) ^ stack
    return fn

# -----------------------------------------------------------------------------

def map_fn(map_fn):
    @_value_fn('map_fn(...)')
    def fn(v:Value[Any]) -> Value[Any]:
        val, stack = v.unstack(1)
        try:
            return Value(map_fn(val)) ^ stack
        except Exception:
            return Message('Error mapping: {}'.format(val)) ^ stack
    return fn

def replace_na(replace_value):
    @_value_fn('replace_na(' + replace_value + ')')
    def fn(v:Value[Any]) -> Value[Any]:
        val, stack = v.unstack(1)
        return Value(replace_value if is_na(val) else val) ^ stack
    return fn

# -----------------------------------------------------------------------------

def stack_sum():
    @_value_fn('stack_sum')
    def fn(v:Value[float|int]) -> Value[float|int]:
        return Value(reduce(operator.add, v.values, 0))
    return fn

def stack_product():
    @_value_fn('stack_product')
    def fn(v:Value[float|int]) -> Value[float|int]:
        return Value(reduce(operator.mul, v.values, 1))
    return fn

def stack_concat():
    @_value_fn('stack_concat')
    def fn(v:Value[str]) -> Value[str]:
        return Value(reduce(operator.concat, v.values, ''))
    return fn

def stack_reverse():
    @_value_fn('stack_reverse')
    def fn(v:Value[Any]) -> Value[Any]:
        return Value(list(reversed(v.values)))
    return fn

def stack_map_fn(map_fn):
    @_value_fn('stack_map_fn(...)')
    def fn(v:Value[Any]) -> Value[Any]:
        return Value(list(map(map_fn, v.values)))
    return fn

def stack_replace_na(replace_value):
    @_value_fn('stack_replace_na(' + replace_value + ')')
    def fn(v:Value) -> Value:
        return Value([(replace_value if is_na(x) else x) for x in v.values])
    return fn

# -----------------------------------------------------------------------------

_META_STR_MATCH_GROUPS = 'groups'

def if_str_match(regexp:str, else_if:bool=False):
    keys = [part.split('>')[0] for part in regexp.split('(?P<')[1:]]

    def test_valid_fn(v):
        text, stack = v.unstack(1)
        m = re.search(regexp, text)
        test = m is not None
        test_data = m
        return test, test_data

    def if_true_fn(v, test_data):
        text, stack = v.unstack(1)
        m = test_data
        fields = {}
        for key in keys:
            try:
                fields[key] = m.group(key)
            except:
                fields[key] = ''
        v[_META_STR_MATCH_GROUPS] = fields
        return v

    def if_false_fn(v, test_data): return v

    fn_title = ('el' if else_if else '') + 'if_str_match'
    fn_title += '(...)'
    return _if_value_valid_fn(fn_title, test_valid_fn,
                              if_true_fn, if_false_fn, else_if)

def elif_str_match(regexp:str, else_if=True):
    return if_str_match(regexp, else_if)

def format_str_by_groups(fmt_str:str):
    @_value_fn('format_str_by_groups(' + fmt_str + ')')
    def fn(v:Value[str]) -> Value[str]:
        if _check_break_fn(v): return v
        text, stack = v.unstack(1)
        if _META_STR_MATCH_GROUPS in v:
            return Value(fmt_str.format(**v[_META_STR_MATCH_GROUPS])) ^ stack
        else:
            return Value(text) ^ stack
    return fn

# -----------------------------------------------------------------------------

def if_value_greater_than(greater_than:int|float, else_if=False):
    def test_valid_fn(v):
        value, stack = v.unstack(1)
        test = value > greater_than
        test_data = None
        return test, test_data

    def if_true_fn(v, test_data): return v

    def if_false_fn(v, test_data): return v

    fn_title = ('el' if else_if else '') + 'if_value_greater_than'
    fn_title += '({})'.format(greater_than)
    return _if_value_valid_fn(fn_title, test_valid_fn,
                              if_true_fn, if_false_fn, else_if)

def elif_value_greater_than(greater_than:int|float, else_if=True):
    return if_value_greater_than(greater_than, else_if)

def if_value_greater_equal_than(greater_equal_than:int|float, else_if=False):
    def test_valid_fn(v):
        value, stack = v.unstack(1)
        test = value >= greater_equal_than
        test_data = None
        return test, test_data

    def if_true_fn(v, test_data): return v

    def if_false_fn(v, test_data): return v

    fn_title = ('el' if else_if else '') + 'if_value_greater_equal_than'
    fn_title += '({})'.format(greater_equal_than)
    return _if_value_valid_fn(fn_title, test_valid_fn,
                              if_true_fn, if_false_fn, else_if)

def elif_value_greater_equal_than(greater_equal_than:int|float, else_if=True):
    return if_value_greater_equal_than(greater_equal_than, else_if)

def if_value_less_than(less_than:int|float, else_if=False):
    def test_valid_fn(v):
        value, stack = v.unstack(1)
        test = value < less_than
        test_data = None
        return test, test_data

    def if_true_fn(v, test_data): return v

    def if_false_fn(v, test_data): return v

    fn_title = ('el' if else_if else '') + 'if_value_less_than'
    fn_title += '({})'.format(less_than)
    return _if_value_valid_fn(fn_title, test_valid_fn,
                              if_true_fn, if_false_fn, else_if)

def elif_value_less_than(less_than:int|float, else_if=True):
    return if_value_less_than(less_than, else_if)

def if_value_less_equal_than(less_equal_than:int|float, else_if=False):
    def test_valid_fn(v):
        value, stack = v.unstack(1)
        test = value <= less_equal_than
        test_data = None
        return test, test_data

    def if_true_fn(v, test_data): return v

    def if_false_fn(v, test_data): return v

    fn_title = ('el' if else_if else '') + 'if_value_less_equal_than'
    fn_title += '({})'.format(less_equal_than)
    return _if_value_valid_fn(fn_title, test_valid_fn,
                              if_true_fn, if_false_fn, else_if)

def elif_value_less_equal_than(less_equal_than:int|float, else_if=True):
    return if_value_less_equal_than(less_equal_than, else_if)

def if_value_equal_to(equal_to:int|float, else_if=False):
    def test_valid_fn(v):
        value, stack = v.unstack(1)
        test = value == equal_to
        test_data = None
        return test, test_data

    def if_true_fn(v, test_data): return v

    def if_false_fn(v, test_data): return v

    fn_title = ('el' if else_if else '') + 'if_value_equal_to'
    fn_title += '({})'.format(equal_to)
    return _if_value_valid_fn(fn_title, test_valid_fn,
                              if_true_fn, if_false_fn, else_if)

def elif_value_equal_to(equal_to:int|float, else_if=True):
    return if_value_equal_to(equal_to, else_if)

# -----------------------------------------------------------------------------
