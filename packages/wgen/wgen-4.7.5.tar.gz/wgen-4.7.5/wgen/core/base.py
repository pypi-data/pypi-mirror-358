from itertools import product
from rich.progress import (
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    MofNCompleteColumn
)
from .charset import charset2string

BANNER = '''
██╗    ██╗ ██████╗ ██████╗ ██████╗ ██╗     ██╗███████╗████████╗     ██████╗ ███████╗███╗   ██╗
██║    ██║██╔═══██╗██╔══██╗██╔══██╗██║     ██║██╔════╝╚══██╔══╝    ██╔════╝ ██╔════╝████╗  ██║
██║ █╗ ██║██║   ██║██████╔╝██║  ██║██║     ██║███████╗   ██║       ██║  ███╗█████╗  ██╔██╗ ██║
██║███╗██║██║   ██║██╔══██╗██║  ██║██║     ██║╚════██║   ██║       ██║   ██║██╔══╝  ██║╚██╗██║
╚███╔███╔╝╚██████╔╝██║  ██║██████╔╝███████╗██║███████║   ██║       ╚██████╔╝███████╗██║ ╚████║
 ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝╚══════╝   ╚═╝        ╚═════╝ ╚══════╝╚═╝  ╚═══╝
'''
DEFAULT_CHAR = charset2string('0aA@')

def estimate_file_size(chrs: str, min_length: int, max_length: int) -> int:
    total_size = 0
    for n in range(min_length, max_length + 1):
        if len(chrs) == 0:
            continue
        sample = (chrs[0] * n + '\n').encode('utf-8')
        line_size = len(sample)
        count = len(chrs) ** n
        total_size += line_size * count
    return total_size

def human_readable(file_size: int) -> str:
    unit = ['B', 'KB', 'MB', 'GB', 'TB']
    index = 0
    size = file_size
    while size > 1024 and index < len(unit) - 1:
        size /= 1024
        index += 1
    return f'{size:.2f}{unit[index]}'

def pass_yield(n: int, chars: str, start: int, end: int):
    base = len(chars)
    for k in range(start, end):
        password = []
        remaining = k
        for _ in range(n):
            remaining, idx = divmod(remaining, base)
            password.append(chars[idx])
        yield ''.join(reversed(password))

def idx2str(index: int, chars_str: str, length: int) -> str:
    chars = list(chars_str)
    base = len(chars)
    result = []
    for _ in range(length):
        index, rem = divmod(index, base)
        result.append(chars[rem])
    return ''.join(reversed(result))

def gen_chunk(args: list) -> str:
    chrs, n, start, end = args
    batch = []
    for idx, chars in enumerate(product(chrs, repeat=n)):
        if idx < start:
            continue
        if idx >= end:
            break
        batch.append(''.join(chars) + '\n')
    return ''.join(batch)

def split_idx(total: int, processes: int) -> list:
    if processes == 0 or total == 0:
        return []
    chunk_size = total // processes
    remainder = total % processes
    indexes = []
    start = 0
    for i in range(processes):
        end = start + chunk_size
        if i < remainder:
            end += 1
        if start >= total:
            break
        if end > total:
            end = total
        indexes.append((start, end))
        start = end
    return indexes

def get_pbar() -> list:
    return [
        TextColumn('[progress.description]{task.description}'),
        BarColumn(),
        MofNCompleteColumn(),
        TextColumn('•'),
        TimeRemainingColumn()
    ]
