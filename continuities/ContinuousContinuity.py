from idataframe.continuities.BaseContinuity import BaseContinuity
from idataframe.distributions.ContinuousDistribution import ContinuousDistribution

__all__ = ['ContinuousContinuity']


class ContinuousContinuity(BaseContinuity):
    """
    Continuous base continuity.
    """

    def __init__(self):
        super().__init__()

    def fitDistribution(self, *args, **kwargs):
        series = self.series  # uses BaseType class
        distr = ContinuousDistribution.from_pandas_series(series, *args, **kwargs)
        return distr





