import pandas as pd

from idataframe.itypes.BaseIType import BaseIType
from idataframe.scales.OrdinalScale import OrdinalScale
from idataframe.fields.StrField import StrField
from idataframe.continuities.DiscreteContinuity import DiscreteContinuity

__all__ = ['Grade']


# -----------------------------------------------------------------------------


class Grade(BaseIType, OrdinalScale, DiscreteContinuity):
    """
    Ordered text.
    """

    RE_GRADE = r".*"

    def __init__(self, series:pd.Series, fields=None):
        if fields is None:   # Grade type called directly
            BaseIType.__init__(self, series, (
                ('grade', StrField()),
            ))
        else:   # subtype of Grade called
            BaseIType.__init__(self, series, fields)
        OrdinalScale.__init__(self)
        DiscreteContinuity.__init__(self)

        if fields is None:
            self.add_match(name = 'grade',
                       regexp = r"^(?P<grade>{})$".format(self.RE_GRADE),
                       str_format = '{grade}')


    @classmethod
    def from_test_data(cls, *args, **kwargs):
        return cls(pd.Series([value.strip() for value in """
            i
            ii
            iii
            iv
            v
            vi
            vii
            viii
            ix
            x
        """.strip().split('\n')]), *args, **kwargs)