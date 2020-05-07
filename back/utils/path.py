import pathlib
import typing as t
from collections import namedtuple


__all__ = [
    'File',
    'nearby'
]


class File(namedtuple('File', 'name ext')):
    __slots__ = ()

    def __str__(self):
        return '.'.join((str(self.name), self.ext))


def nearby(for_file: str, join_path: t.Union[str, t.Tuple, None] = None) -> pathlib.Path:
    parent_path = pathlib.Path(for_file).parent.absolute()
    if join_path:
        if isinstance(join_path, tuple):
            for join_sub_path in join_path:
                parent_path = parent_path.joinpath(join_sub_path)
        else:
            assert isinstance(join_path, str)
            parent_path = parent_path.joinpath(join_path)
    return parent_path
