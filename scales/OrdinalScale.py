from idataframe.scales.NominalScale import NominalScale

__all__ = ['OrdinalScale']


class OrdinalScale(NominalScale):
    """
    Ordinal base scale.
    """

    def __init__(self):
        super().__init__()

