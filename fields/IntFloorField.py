import numpy as np

from idataframe.fields.BaseField import BaseField

__all__ = ['IntFloorField']


class IntFloorField(BaseField):
    series_type = 'Int64'    # Pandas Series type; don't use `int` as type because then it can't contain NaN values

    def __init__(self, parse_fn=None):
        super().__init__(parse_fn)

    def str_to_type_fn(self, value):
        return int(np.floor(float(value)))