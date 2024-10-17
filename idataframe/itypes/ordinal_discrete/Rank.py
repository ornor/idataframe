import pandas as pd

from idataframe.itypes.BaseIType import BaseIType
from idataframe.scales.OrdinalScale import OrdinalScale
from idataframe.fields.IntField import IntField
from idataframe.continuities.DiscreteContinuity import DiscreteContinuity

__all__ = ['Rank']


# -----------------------------------------------------------------------------


class Rank(BaseIType, OrdinalScale, DiscreteContinuity):
    """
    Ordered numerical values (integers), with no constant interval.
    """

    RE_RANK = r"[\+\-]?[0-9]+"

    def __init__(self, series:pd.Series, fields=None):
        if fields is None:   # Rank type called directly
            BaseIType.__init__(self, series, (
                ('rank', IntField()),
            ))
        else:   # subtype of Rank called
            BaseIType.__init__(self, series, fields)
        OrdinalScale.__init__(self)
        DiscreteContinuity.__init__(self)

        if fields is None:
            self.add_match(name = 'rank',
                       regexp = r"^(?P<rank>{})$".format(self.RE_RANK),
                       str_format = '{rank}')


    @classmethod
    def from_test_data(cls, *args, **kwargs):
        return cls(pd.Series([
                1, 2, 3, 5, 7, 11, 13, 17, 19, 23
            ]), *args, **kwargs)