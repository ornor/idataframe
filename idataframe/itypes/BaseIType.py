from typing import Tuple, Callable
import re
import numpy as np
import pandas as pd

from idataframe.base import *
from idataframe.fields.BaseField import BaseField

__all__ = ['BaseIType']


# -----------------------------------------------------------------------------


class BaseIType(object):
    """
    Base type as foundation of all data types.
    """

    MAX_NR_ERROR_MESSAGES = 20
    COLUMN_NAME_ORIGINAL = '__original__'

    def __init__(self, series:pd.Series, fields:Tuple[Tuple[str, BaseField]]):
        if not type(series) == type(pd.Series([])):
            raise TypeError("Input data must be a Pandas Series object (now input type is {})".format(type(series)))

        if series.empty:
            raise ValueError("Input data is empty (it must be a non empty  Series)")

        if not isinstance(fields, tuple) or not len(fields) > 0 or not isinstance(fields[0], tuple) or not len(fields[0]) == 2:
            raise SyntaxError('Configuration of must be a tuple with at least one tuple containing (name, series_type). Now it\'s: {}'.format(fields))

        for field in fields:
            if not isinstance(field, tuple) or not len(field) == 2 or not isinstance(field[0], str) or not isinstance(field[1], BaseField):
                raise SyntaxError('Configuration syntax is invalid, it should be (name <str>, series_type <SeriesType>). Now it\'s: {}'.format(field))

        self._df = pd.DataFrame({
            self.COLUMN_NAME_ORIGINAL : series
        })

        self._series_name = fields[0][0]
        self._series_type = fields[0][1].series_type
        self._series_str_to_type_fn = fields[0][1].str_to_type_fn
        self._series_post_parse_fn = fields[0][1].post_parse_fn
        self._fields_fields = fields[1:] if len(fields) > 1 else []
        self._pre_parse_fns = []
        self._matches = []
        self._matches_str = []

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    @df.setter
    def df(self, _):
        raise PermissionError("The df property is read only")

    @property
    def is_parsed(self) -> bool:
        return self._series_name in self._df

    @is_parsed.setter
    def is_parsed(self, _):
        raise PermissionError("The is_parsed property is read only")

    @property
    def series(self) -> pd.Series:
        if not self.is_parsed:
            return self._df[self.COLUMN_NAME_ORIGINAL]
        else:
            return self._df[self._series_name]

    @series.setter
    def series(self, _):
        raise PermissionError("The series property is read only")

    def add_pre_parse_fn(self, pre_parse_fn:Callable[[str], str]):
        if not callable(pre_parse_fn):
            raise TypeError("`pre_parse_fn` must be callable (now type is {})".format(type(pre_parse_fn)))

        self._pre_parse_fns.append(pre_parse_fn)

    def reset_matches(self):
        self._matches_str = []

    def add_match(self, name:str, regexp:str, str_format:str):
        if not isinstance(name, str):
            raise TypeError("`name` attribute must be a string (now name type is {})".format(type(name)))

        if not isinstance(regexp, str):
            raise TypeError("`regexp` attribute must be a string (now regexp type is {})".format(type(regexp)))

        if not isinstance(str_format, str):
            raise TypeError("`str_format` attribute must be a string (now str_format type is {})".format(type(str_format)))

        def fn_match(value:str) -> ValueMessages:
            m = re.search(regexp, value)
            if m is not None:
                field_str_values = {}
                field_values = {}
                for field_fields in self._fields_fields:
                    field_name = field_fields[0]
                    field_str_to_type_fn = field_fields[1].str_to_type_fn
                    field_post_parse_fn = field_fields[1].post_parse_fn
                    field_str_value = None
                    try:
                        field_str_values[field_name] = field_post_parse_fn(m.group(field_name))
                        field_values[field_name] = field_str_to_type_fn(field_str_values[field_name])
                    except:
                        field_str_values[field_name] = ''
                try:
                    field_str_values[self._series_name] = self._series_post_parse_fn(m.group(self._series_name))
                except:
                    pass
                value = self._series_str_to_type_fn(self._series_post_parse_fn(str_format.format(**field_str_values)))
                return_value = (value, field_values)
                return Value(return_value)
            else:
                return ValueMessage(None, 'value can\'t be parsed: {}'.format(value))

        self._matches_str.append('match {:>2} :: {:<24} :: {}'.format(str(len(self._matches) + 1), name, regexp))
        self._matches.append((name, fn_match))

    def _parse_str_value(self, original_value:str) -> ValueMessages:
        parsed_value = None
        messages = []
        for match_name, fn in self._matches:
            match_value, match_messages = fn(original_value).prefix_messages('match {:<30} :: '.format(match_name)).items
            if match_value is not None:
                parsed_value = match_value
                messages = []
                break
            else:
                messages = messages + match_messages
        return ValueMessages(parsed_value, messages)

    def parse(self, max_values:int=None, max_messages:int=MAX_NR_ERROR_MESSAGES, verbose=True) -> VMList:
        value_messages_list = VMList()
        nr_messages = 0
        self._df[self._series_name] = np.nan
        self._df[self._series_name] = self._df[self._series_name].astype(self._series_type)

        for field_fields in self._fields_fields:
            field_name = field_fields[0]
            field_type = field_fields[1].series_type
            self._df[field_name] = np.nan
            self._df[field_name] = self._df[field_name].astype(field_type)

        for index, value in self._df[self.COLUMN_NAME_ORIGINAL].items():
            if max_values is not None and isinstance(max_values, int) and index > max_values:
                value_messages_list.add(
                        Message('\nreached maximum number of values, parsing proces aborted...\n\nusing matches:\n{}\n'.format('\n'.join(self._matches_str))))
                break
            if max_messages is not None and isinstance(max_messages, int) and nr_messages > max_messages:
                value_messages_list.add(
                        Message('\nreached maximum number of messages, parsing proces aborted...\n\nusing matches:\n{}\n'.format('\n'.join(self._matches_str))))
                break

            value_str = str(value).strip()
            for pre_parse_fn in self._pre_parse_fns:
                value_str = pre_parse_fn(value_str)
            value_messages = self._parse_str_value(value_str)

            if len(value_messages.messages) > 0:
                nr_messages = nr_messages + len(value_messages.messages)
                value_messages_list.add(value_messages.prefix_messages('index {:>4} :: '.format(index)))
            parsed_output = value_messages.value
            if parsed_output is not None:
                parsed_value, parsed_field_values = parsed_output
                self._df.loc[index, self._series_name] = parsed_value
                for field_name, field_value in parsed_field_values.items():
                    if field_name not in self._df.columns:
                        raise KeyError('The field name \'{}\' is not defined in field_names tuple')
                    self._df.loc[index, field_name] = field_value

            if index == self._df.shape[0] - 1:  # last item
                value_messages_list.add(
                        Message('\nusing matches:\n{}\n'.format('\n'.join(self._matches_str))))

        if verbose:
            print('\n'.join(value_messages_list.messages))

        return value_messages_list

    def __str__(self):
        return 'Dataframe property:\n' + str(self.df)

    @classmethod
    def from_test_data(cls, *args, **kwargs):
        return cls(pd.Series([np.nan]), *args, **kwargs)



