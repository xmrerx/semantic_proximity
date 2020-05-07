__all__ = [
    'AttrDict'
]


class AttrDict(dict):
    def __init__(self, *args, **kwargs) -> None:
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self
