from typing import Dict

import pandas as pd

from idataframe.itypes.BaseIType import BaseIType

__all__ = ['DataFrame']


# -----------------------------------------------------------------------------


class DataFrame(object):
    """
    Intention Based DataFrame. Based on the DataFrame class of Pandas.
    """

    def __init__(self, dataframe:pd.DataFrame):
        if not type(dataframe) == type(pd.DataFrame({})):
            raise TypeError("Input data must be a Pandas DataFrame object" +
                            " (now input type is {})".format(type(dataframe)))

        self._df = pd.DataFrame({})
        self._df_original = dataframe
        self._cols = {}  # dict of all the IType objects

    @property
    def df(self) -> pd.DataFrame:
        dataframe = pd.DataFrame({})
        for name in self._cols:
            dataframe[name] = self._cols[name].series

        return dataframe

    @df.setter
    def df(self, _):
        raise PermissionError("The df property is read only")

    def  __getitem__(self, name):
        if not name in self._cols:
            raise KeyError("The name '{}' has not been registered.".format(name))
        return self._cols[name]

    def register(self, series_types:Dict[str, BaseIType]):
        for series_name, series_type in series_types.items():
            if series_name in self._cols:
                raise KeyError("The name '{}' already exists.".format(series_name))
            if not series_name in self._df_original:
                raise KeyError("The name '{}' has not been found in Pandas DataFrame.".format(series_name))
            if not issubclass(series_type, BaseIType):
                raise TypeError("The type of '{}' is not a valid IType".format(series_type))

            self._cols[series_name] = series_type(self._df_original[series_name])

    def parse_all(self, *args, **kwargs):
        for col in self._cols:
            print(80*'-'+'\n\n'+'parsing \'{}\''.format(col))
            self._cols[col].parse(*args, **kwargs)
        print(80*'-'+'\n')