from idataframe.scales.IntervalScale import IntervalScale

__all__ = ['RatioScale']


class RatioScale(IntervalScale):
    """
    Ratio base scale.
    """

    def __init__(self):
        super().__init__()
