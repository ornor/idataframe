import pandas as pd

from idataframe.itypes.BaseIType import BaseIType
from idataframe.scales.RatioScale import RatioScale
from idataframe.fields.FloatField import FloatField
from idataframe.continuities.ContinuousContinuity import ContinuousContinuity

__all__ = ['Balance']


# -----------------------------------------------------------------------------


class Balance(BaseIType, RatioScale, ContinuousContinuity):
    """
    Positive or negative float data type.
    """

    RE_BALANCE = r"[\-+]?(?:[0-9]+|[0-9]+\.[0-9]+|\.[0-9]+)(?:[eE][\-+]?[0-9]+)?"

    def __init__(self, series:pd.Series, fields=None):
        if fields is None:   # Balance type called directly
            BaseIType.__init__(self, series, (
                ('balance',  FloatField()),
            ))
        else:   # subtype of Balance called
            BaseIType.__init__(self, series, fields)
        RatioScale.__init__(self)
        ContinuousContinuity.__init__(self)

        if fields is None:
            self.add_match(name = 'balance',
                       regexp = r"^(?P<balance>{})$".format(self.RE_BALANCE),
                       str_format = '{balance}')

    @classmethod
    def from_test_data(cls, *args, **kwargs):
        return cls(pd.Series([
                -8.1, -4.56, 0, 1, 2, 3.2, 5.8, 7, 11, 13, 17, 19, 23
            ]), *args, **kwargs)