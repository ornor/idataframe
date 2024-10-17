import pandas as pd

from idataframe.itypes.BaseIType import BaseIType
from idataframe.scales.NominalScale import NominalScale
from idataframe.fields.StrField import StrField
from idataframe.continuities.DiscreteContinuity import DiscreteContinuity

__all__ = ['Text']


# -----------------------------------------------------------------------------


class Text(BaseIType, NominalScale, DiscreteContinuity):
    """
    Unordered text (mostly unique values).
    """

    RE_TEXT = r".*"

    def __init__(self, series:pd.Series, fields=None):
        if fields is None:   # Text type called directly
            BaseIType.__init__(self, series, (
                ('text', StrField()),
            ))
        else:   # subtype of Text called
            BaseIType.__init__(self, series, fields)
        NominalScale.__init__(self)
        DiscreteContinuity.__init__(self)

        if fields is None:
            self.add_match(name = 'text',
                       regexp = r"^(?P<text>{})$".format(self.RE_TEXT),
                       str_format = '{text}')


    @classmethod
    def from_test_data(cls, *args, **kwargs):
        return cls(pd.Series([value.strip() for value in """
            monkey
            nut
            Mies
            Wim
            sister
            Jet
        """.strip().split('\n')]), *args, **kwargs)