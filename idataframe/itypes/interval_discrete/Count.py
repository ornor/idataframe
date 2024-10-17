import numpy as np
import pandas as pd

from idataframe.itypes.BaseIType import BaseIType
from idataframe.scales.IntervalScale import IntervalScale
from idataframe.fields.IntField import IntField
from idataframe.fields.IntFloorField import IntFloorField
from idataframe.itypes.ratio_continuous.Amount import Amount
from idataframe.continuities.DiscreteContinuity import DiscreteContinuity

__all__ = ['Count']


# -----------------------------------------------------------------------------


class Count(BaseIType, IntervalScale, DiscreteContinuity):
    """
    Positive integer data type.
    """

    RE_COUNT = r"\+?[0-9]+"
    RE_AMOUNT = Amount.RE_AMOUNT   # positive float, convert to int

    def __init__(self, series:pd.Series, fields=None,
                       round_float_to_floor:bool=False):
        if fields is None:   # Count type called directly
            BaseIType.__init__(self, series, (
                ('count',  IntFloorField() if round_float_to_floor else IntField() ),
            ))
        else:   # subtype of Count called
            BaseIType.__init__(self, series, fields)
        IntervalScale.__init__(self)
        DiscreteContinuity.__init__(self)

        if fields is None:
            self.add_match(name = 'count',
                       regexp = r"^(?P<count>{})$".format(self.RE_COUNT),
                       str_format = '{count}')

            self.add_match(name = 'amount -> count',
                       regexp = r"^(?P<count>{})$".format(self.RE_AMOUNT),
                       str_format = '{count}')

    @classmethod
    def from_test_data(cls, *args, **kwargs):
        return cls(pd.Series([
                12, 53, 76, 1, 3, np.nan, 12, -5, 7.67, 8.999999, 9.0000001
            ]), *args, **kwargs)