import pandas as pd
import numpy as np

from idataframe.itypes.ratio_continuous.Balance import Balance
from idataframe.fields.FloatField import FloatField

__all__ = ['Amount']


# -----------------------------------------------------------------------------


class Amount(Balance):
    """
    Positive float data type. Subclass of Balance.
    """

    RE_AMOUNT = r"\+?(?:[0-9]+|[0-9]+\.[0-9]+|\.[0-9]+)(?:[eE][\-+]?[0-9]+)?"

    def __init__(self, series:pd.Series, fields=None):
        if fields is None:   # Amount type called directly
            Balance.__init__(self, series, (
                ('amount',  FloatField()),
            ))
        else:   # subtype of Amount called
            Balance.__init__(self, series, fields)

        if fields is None:
            self.add_match(name = 'amount',
                       regexp = r"^(?P<amount>{})$".format(self.RE_AMOUNT),
                       str_format = '{amount}')


    @classmethod
    def from_test_data(cls, *args, **kwargs):
        return cls(pd.Series([
                1, 2, 3.2, 5.8, 7, 11, np.nan, 13, 17, 19, 23
            ]), *args, **kwargs)