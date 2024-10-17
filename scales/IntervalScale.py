from idataframe.scales.OrdinalScale import OrdinalScale

__all__ = ['IntervalScale']


class IntervalScale(OrdinalScale):
    """
    Interval base scale.
    """

    def __init__(self):
        super().__init__()

