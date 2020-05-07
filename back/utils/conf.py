import configparser
import typing as t
from pathlib import Path

from .struct import AttrDict
from .path import nearby


__all__ = [
    'T_Conf',
    'Conf'
]


T_Conf = t.TypeVar('T_Conf', bound='Conf')


class Conf(AttrDict):
    def __init__(self, conf, entry_point_file: str):
        super().__init__(conf)
        self._entry_point_file = entry_point_file

    def path(self, path_name, extra_join: t.Union[str, t.List, None] = None) -> Path:
        paths = [self.PATH[path_name]]
        if extra_join is not None:
            if isinstance(extra_join, str):
                extra_join = [extra_join]
            paths += extra_join
        return nearby(self._entry_point_file, tuple(paths))

    @classmethod
    def get(cls, entry_point_file: str, conf_file_name: str = 'config.ini') -> T_Conf:
        conf = configparser.ConfigParser()
        conf.read(nearby(entry_point_file, conf_file_name))
        if '_entry_point_file' in conf:
            raise RuntimeError('`_entry_point_file` is reserved for Conf class.')
        if 'path' in conf:
            raise RuntimeError('`path` is reserved for Conf class.')
        return cls(conf, entry_point_file)
