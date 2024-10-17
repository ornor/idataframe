from idataframe.continuities.BaseContinuity import BaseContinuity

__all__ = ['DiscreteContinuity']


class DiscreteContinuity(BaseContinuity):
    """
    Discrete base continuity.
    """

    def __init__(self):
        super().__init__()
