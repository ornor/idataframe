import pandas as pd

from idataframe.itypes.BaseIType import BaseIType
from idataframe.scales.NominalScale import NominalScale
from idataframe.fields.StrField import StrField
from idataframe.continuities.DiscreteContinuity import DiscreteContinuity

__all__ = ['Label']


# -----------------------------------------------------------------------------


class Label(BaseIType, NominalScale, DiscreteContinuity):
    """
    Unordered categorical text (less different values).
    """

    RE_LABEL = r".*"

    def __init__(self, series:pd.Series, fields=None):
        if fields is None:   # Label type called directly
            BaseIType.__init__(self, series, (
                ('label', StrField()),
            ))
        else:   # subtype of Label called
            BaseIType.__init__(self, series, fields)
        NominalScale.__init__(self)
        DiscreteContinuity.__init__(self)

        if fields is None:
            self.add_match(name = 'label',
                       regexp = r"^(?P<label>{})$".format(self.RE_LABEL),
                       str_format = '{label}')


    @classmethod
    def from_test_data(cls, *args, **kwargs):
        return cls(pd.Series([value.strip() for value in """
            A+
            A-
            B+
            B-
            O+
            O-
            AB+
            AB-
        """.strip().split('\n')]), *args, **kwargs)