import io
import os
import pathlib
import typing as t
from enum import IntEnum
from itertools import islice


__all__ = [
    'get_offsets',
    'get_sentence',
    'get_headlines',
    'get_content',
    'save_content',
    'SortBy',
    'list_dir_files',
    'walk_sentences'
]


def get_offsets(file: t.IO, encoding: str = None) -> int:
    line_offsets = []
    offset = 0
    file.seek(0)
    for line in file:
        line_offsets.append(offset)
        offset += len(line.encode(encoding)) if encoding else len(line)
    return line_offsets


def get_sentence(file_path: str, offset: int) -> str:
    sentence = ''
    with io.open(file_path, 'r', encoding='utf8') as file:
        file.seek(offset)
        sentence = file.readline()
    return sentence


def get_headlines(file_path: str, rows_number: int = 1) -> t.List:
    with io.open(file_path, 'r', encoding='utf8') as file:
        try:
            head = list(islice(file, rows_number))
        except StopIteration:
            head = ['']
    return head


def get_content(file_path: str) -> str:
    content = ''
    with io.open(file_path, 'r', encoding='utf8') as file:
        content = file.read()
    return content


def save_content(file_path: str, content: t.Union[str, t.List]) -> None:
    with io.open(file_path, 'w', encoding='utf8') as file:
        if not isinstance(content, str):
            content = "\n".join(content)
        file.write(content)


SortBy = IntEnum('SortBy', 'name date_desc')


def list_dir_files(dir_path: pathlib.Path, sort: SortBy = SortBy.name) -> t.List:
    try:
        files = next(os.walk(dir_path))[2]
    except StopIteration:
        files = []
    if sort == SortBy.name:
        files.sort()
    else:
        assert sort == SortBy.date_desc
        files.sort(key=lambda x: os.path.getmtime(dir_path.joinpath(x)), reverse=True)
    return files


def walk_sentences(
    source_dir: pathlib.Path,
    ext: str,
    *,
    stop: t.Optional[int] = None,
    without_file: t.Optional[str] = None,
    split_line: bool = True
) -> t.List:
    for file_num, file_path in enumerate(list_dir_files(source_dir)):
        if without_file == file_path:
            continue
        with io.open(source_dir.joinpath(file_path), 'r', encoding='utf8') as file:
            for line_id, line in enumerate(file):
                file_id = file_path.replace('.' + ext, '')
                if split_line:
                    line = line.strip().split()
                yield (file_id, line_id, line)
                if stop and file_num >= stop:
                    raise StopIteration


def walk_sentences_simple(
    source_dir: pathlib.Path,
    ext: str,
    *,
    stop: t.Optional[int] = None,
    without_file: t.Optional[str] = None,
    split_line: bool = True
) -> t.List:
    for sentence_map in walk_sentences(**locals()):
        file_id, line_id, words = sentence_map
        yield words
