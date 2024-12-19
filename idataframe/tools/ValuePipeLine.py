from __future__ import annotations
import re
import functools
from typing import Callable, Any, Tuple, List
import operator
import textwrap

from idataframe.tools.Value import is_na, na, Value, Message


class ValuePipeLine(object):
    META_DEBUG = 'debug'
    META_IF = 'if'
    META_IF_FALSE = 0
    META_IF_TRUE  = 1
    META_IF_PERMANENT_FALSE = 2
    META_STR_MATCH_GROUPS = 'groups'

    def __init__(self):
        self._pipes = []

    def _add_pipe(self, fn):
        self._pipes.append(fn)

    def __call__(self, v:Any|Value[Any]) -> Value[Any]:
        if not isinstance(v, Value):
            v = Value(v)
        for fn in self._pipes:
            v = v | fn
        return v

    # -------------------------------------------------------------------------

    def _set_if(self, v:Value, if_value:int) -> Value:
        """
        Sets META_IF as a new level.
        v[META_IF] contains list containing if-values (bools) of each nested level
        """
        if self.META_IF not in v:
            v[self.META_IF] = [if_value]
        else:
            if len(v[self.META_IF]) > 0: # create extra nested level
                v[self.META_IF].insert(0, if_value)
            else:
                v[self.META_IF].append(if_value)
        return v

    def _replace_if(self, v:Value, if_value:int) -> Value:
        """
        Replace META_IF in current level.

        v[META_IF] contains list containing if-values (bools) of each nested
        level.
        """
        if self.META_IF not in v or len(v[self.META_IF]) < 1:
            return Message('Error: no if-statement found.') ^ v.values
        else:
            v[self.META_IF][0] = if_value
        return v

    def _get_if(self, v:Value) -> int:
        """
        Gets META_IF value or None is no if-level is set.
        """
        if self.META_IF not in v or len(v[self.META_IF]) < 1:
            return None
        else:
            return v[self.META_IF][0]

    def _check_break_fn(self, v:Value[Any]) -> bool:
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
        if_value = self._get_if(v)
        return (if_value == self.META_IF_FALSE
                or if_value == self.META_IF_PERMANENT_FALSE)

    def _register_pipe_fn(self,
                  fn_name:str,
                  fn_args:Any|List[Any]=None,
                  manual_break:bool=False):
        repr_left = repr(Value('dummy')).split('Value')[0]
        title_string = str(fn_name) + '('
        if fn_args is not None:
            if not isinstance(fn_args, list):
                fn_args = [fn_args]
            sep = ', '
            for fn_arg in fn_args:
                fn_arg_str = repr(fn_arg)
                if len(fn_arg_str) > 40:
                    title_string += "{} ... {}".format(
                            fn_arg_str[:19], fn_arg_str[-19:])
                else:
                    title_string += "{}".format(fn_arg_str)
                title_string += sep
            title_string = title_string[:-len(sep)]
        title_string += ')'
        def decorator(fn):
            @functools.wraps(fn)
            def wrapper(v:Value[Any]) -> Value[Any]:
                if self._check_break_fn(v) and not manual_break:
                    return_value = v
                else:
                    return_value = fn(v)    # excecute pipe
                    if self.META_DEBUG in v:
                        if_value = self._get_if(v)
                        if (if_value == self.META_IF_TRUE
                            or if_value is None):
                            if v[self.META_DEBUG] == True:
                                print('• {}\n    {}'.format(
                                    title_string,
                                    '\n    '.join(textwrap.wrap(repr(
                                    return_value).lstrip(repr_left), width=50))
                                ))
                            else:
                                print('• {}\n    {}'.format(
                                    title_string, repr(return_value.value)
                                ))
                        else:
                            print('- {}'.format(title_string))
                return return_value
            self._add_pipe(wrapper)
            return wrapper
        return decorator

    def _if_value_valid_fn(self,
                           fn_title:str,
                           fn_args:Any|List[Any],
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
        @self._register_pipe_fn(fn_title, fn_args, manual_break=True)
        def fn(v: Value[Any]) -> Value[Any]:
            v = ((self._replace_if(v, self.META_IF_TRUE)
                 if self._get_if(v) == self.META_IF_FALSE
                 else (self._replace_if(v, self.META_IF_PERMANENT_FALSE)
                       if self._get_if(v) == self.META_IF_TRUE else v))
                if else_if else v)
            if self._check_break_fn(v): return v
            valid, test_data = test_valid_fn(v)
            if valid:
                v = if_true_fn(v, test_data)
                return (self._replace_if(v, self.META_IF_TRUE) if else_if
                        else self._set_if(v, self.META_IF_TRUE))
            else:
                v = if_false_fn(v, test_data)
                return (self._replace_if(v, self.META_IF_FALSE) if else_if
                        else self._set_if(v, self.META_IF_FALSE))
        return fn

    # -------------------------------------------------------------------------

    def debug(self,
              show_value_obj:bool=False,
              set_on:bool=True) -> ValuePipeLine:
        """
        Turn debug mode to on or off.

        Parameters
        ----------
        set_on : bool, optional
            True = on, False = off. The default is True.

        Returns
        -------
        ValuePipeLine
            self
        """
        repr_left = repr(Value('dummy')).split('Value')[0]
        def fn(v:Value[Any]):
            if set_on:
                if show_value_obj:
                    print('\nDEBUG ON\n    {}'.format(
                        repr(v).lstrip(repr_left)))
                else:
                    print('\nDEBUG ON\n    {}'.format(
                        repr(v.value)))
                v[self.META_DEBUG] = show_value_obj
            else:
                if self.META_DEBUG in v:
                    del v[self.META_DEBUG]
                if show_value_obj:
                    print('\nDEBUG OFF\n    {}'.format(
                        repr(v).lstrip(repr_left)))
                else:
                    print('\nDEBUG OFF\n    {}'.format(
                        repr(v.value)))
            return v
        self._add_pipe(fn)
        return self

    def log(self, txt:str=None):
        @self._register_pipe_fn('log', txt)
        def fn(v:Value[Any]) -> Value[Any]:
            if txt is None:
                print(v)
            else:
                print(txt)
            return v
        return self

    # -------------------------------------------------------------------------

    def else_(self):
        @self._register_pipe_fn('else_', manual_break=True)
        def fn(v:Value[Any]) -> Value[Any]:
            if self.META_IF not in v or len(v[self.META_IF]) < 1:
                return Message('Error: no if-statement found.') ^ v.values
            else:
                if_value = v[self.META_IF][0]
                if if_value == self.META_IF_TRUE:
                    v[self.META_IF][0] = self.META_IF_FALSE
                elif if_value == self.META_IF_FALSE:
                    v[self.META_IF][0] = self.META_IF_TRUE
                elif if_value == self.META_IF_PERMANENT_FALSE:
                    pass # leave value permanent false
                return v
        return self

    def end_if(self):
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
        @self._register_pipe_fn('end_if', manual_break=True)
        def fn(v:Value[Any]) -> Value[Any]:
            if self.META_IF not in v or len(v[self.META_IF]) < 1:
                return Message('Error: no if-statement found.') ^ v.values
            else:
                if len(v[self.META_IF]) > 1:
                    _ = v[self.META_IF].pop(0)
                else:
                    del v[self.META_IF]
            return v
        return self

    # -------------------------------------------------------------------------

    def change(self, new_value):
        @self._register_pipe_fn('change', new_value)
        def fn(v:Value[Any]) -> Value[Any]:
            _, stack = v.unstack(1)
            return Value(new_value) ^ stack
        return self

    # -------------------------------------------------------------------------

    def parse_int(self):
        @self._register_pipe_fn('parse_int')
        def fn(v:Value[Any]) -> Value[int]:
            val, stack = v.unstack(1)
            if is_na(val):
                return Value(na) ^ stack
            try:
                return Value(int(val)) ^ stack
            except Exception:
                return Message('Error parsing int: {}'.format(val)) ^ stack
        return self

    def parse_float(self):
        @self._register_pipe_fn('parse_float')
        def fn(v:Value[Any]) -> Value[float]:
            val, stack = v.unstack(1)
            if is_na(val):
                return Value(na) ^ stack
            try:
                return Value(float(val)) ^ stack
            except Exception:
                return Message('Error parsing float: {}'.format(val)) ^ stack
        return self

    def parse_str(self):
        @self._register_pipe_fn('parse_str')
        def fn(v:Value[Any]) -> Value[str]:
            val, stack = v.unstack(1)
            if is_na(val):
                return Value(na) ^ stack
            try:
                return Value(str(val)) ^ stack
            except Exception:
                return Message('Error parsing str: {}'.format(val)) ^ stack
        return self

    # -------------------------------------------------------------------------

    def map_fn(self, map_fn):
        @self._register_pipe_fn('map_fn')
        def fn(v:Value[Any]) -> Value[Any]:
            val, stack = v.unstack(1)
            try:
                return Value(map_fn(val)) ^ stack
            except Exception:
                return Message('Error mapping: {}'.format(val)) ^ stack
        return self

    def replace_na(self, replace_value):
        @self._register_pipe_fn('replace_na', replace_value)
        def fn(v:Value[Any]) -> Value[Any]:
            val, stack = v.unstack(1)
            return Value(replace_value if is_na(val) else val) ^ stack
        return self

    # -------------------------------------------------------------------------

    def stack_sum(self):
        @self._register_pipe_fn('stack_sum')
        def fn(v:Value[float|int]) -> Value[float|int]:
            return Value(functools.reduce(operator.add, v.values, 0))
        return self

    def stack_product(self):
        @self._register_pipe_fn('stack_product')
        def fn(v:Value[float|int]) -> Value[float|int]:
            return Value(functools.reduce(operator.mul, v.values, 1))
        return self

    def stack_concat(self):
        @self._register_pipe_fn('stack_concat')
        def fn(v:Value[str]) -> Value[str]:
            return Value(functools.reduce(operator.concat, v.values, ''))
        return self

    def stack_reverse(self):
        @self._register_pipe_fn('stack_reverse')
        def fn(v:Value[Any]) -> Value[Any]:
            return Value(list(reversed(v.values)))
        return self

    def stack_map_fn(self, map_fn):
        @self._register_pipe_fn('stack_map_fn')
        def fn(v:Value[Any]) -> Value[Any]:
            return Value(list(map(map_fn, v.values)))
        return self

    def stack_replace_na(self, replace_value):
        @self._register_pipe_fn('stack_replace', replace_value)
        def fn(v:Value) -> Value:
            return Value([(replace_value if is_na(x) else x) for x in v.values])
        return self

    # -------------------------------------------------------------------------

    def if_str_match(self, regexp:str, else_if:bool=False):
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
            v[self.META_STR_MATCH_GROUPS] = fields
            return v

        def if_false_fn(v, test_data): return v

        fn_title = ('el' if else_if else '') + 'if_str_match'
        fn_args = regexp
        self._if_value_valid_fn(fn_title, fn_args, test_valid_fn,
                                  if_true_fn, if_false_fn, else_if)
        return self

    def elif_str_match(self, regexp:str, else_if=True):
        return self.if_str_match(regexp, else_if)

    def format_str_by_groups(self, fmt_str:str):
        @self._register_pipe_fn('format_str_by_groups', fmt_str)
        def fn(v:Value[str]) -> Value[str]:
            text, stack = v.unstack(1)
            if self.META_STR_MATCH_GROUPS in v:
                return Value(
                    fmt_str.format(**v[self.META_STR_MATCH_GROUPS])) ^ stack
            else:
                return Value(text) ^ stack
        return self

    # -------------------------------------------------------------------------

    def if_value_greater_than(self, greater_than:int|float, else_if=False):
        def test_valid_fn(v):
            value, stack = v.unstack(1)
            test = value > greater_than
            test_data = None
            return test, test_data

        def if_true_fn(v, test_data): return v

        def if_false_fn(v, test_data): return v

        fn_title = ('el' if else_if else '') + 'if_value_greater_than'
        fn_args = greater_than
        self._if_value_valid_fn(fn_title, fn_args, test_valid_fn,
                                  if_true_fn, if_false_fn, else_if)
        return self

    def elif_value_greater_than(self, greater_than:int|float, else_if=True):
        return self.if_value_greater_than(greater_than, else_if)

    def if_value_greater_equal_than(self, greater_equal_than:int|float, else_if=False):
        def test_valid_fn(v):
            value, stack = v.unstack(1)
            test = value >= greater_equal_than
            test_data = None
            return test, test_data

        def if_true_fn(v, test_data): return v

        def if_false_fn(v, test_data): return v

        fn_title = ('el' if else_if else '') + 'if_value_greater_equal_than'
        fn_args = greater_equal_than
        self._if_value_valid_fn(fn_title, fn_args, test_valid_fn,
                                  if_true_fn, if_false_fn, else_if)
        return self

    def elif_value_greater_equal_than(self, greater_equal_than:int|float,
                                      else_if=True):
        return self.if_value_greater_equal_than(greater_equal_than, else_if)

    def if_value_less_than(self, less_than:int|float, else_if=False):
        def test_valid_fn(v):
            value, stack = v.unstack(1)
            test = value < less_than
            test_data = None
            return test, test_data

        def if_true_fn(v, test_data): return v

        def if_false_fn(v, test_data): return v

        fn_title = ('el' if else_if else '') + 'if_value_less_than'
        fn_args = less_than
        self._if_value_valid_fn(fn_title, fn_args, test_valid_fn,
                                  if_true_fn, if_false_fn, else_if)
        return self

    def elif_value_less_than(self, less_than:int|float, else_if=True):
        return self.if_value_less_than(less_than, else_if)

    def if_value_less_equal_than(self, less_equal_than:int|float,
                                 else_if=False):
        def test_valid_fn(v):
            value, stack = v.unstack(1)
            test = value <= less_equal_than
            test_data = None
            return test, test_data

        def if_true_fn(v, test_data): return v

        def if_false_fn(v, test_data): return v

        fn_title = ('el' if else_if else '') + 'if_value_less_equal_than'
        fn_args = less_equal_than
        self._if_value_valid_fn(fn_title, fn_args, test_valid_fn,
                                  if_true_fn, if_false_fn, else_if)
        return self

    def elif_value_less_equal_than(self, less_equal_than:int|float, else_if=True):
        return self.if_value_less_equal_than(less_equal_than, else_if)

    def if_value_equal_to(self, equal_to:int|float, else_if=False):
        def test_valid_fn(v):
            value, stack = v.unstack(1)
            test = value == equal_to
            test_data = None
            return test, test_data

        def if_true_fn(v, test_data): return v

        def if_false_fn(v, test_data): return v

        fn_title = ('el' if else_if else '') + 'if_value_equal_to'
        fn_args = equal_to
        self._if_value_valid_fn(fn_title, fn_args, test_valid_fn,
                                  if_true_fn, if_false_fn, else_if)
        return self

    def elif_value_equal_to(self, equal_to:int|float, else_if=True):
        return self.if_value_equal_to(equal_to, else_if)

    # -----------------------------------------------------------------------------
