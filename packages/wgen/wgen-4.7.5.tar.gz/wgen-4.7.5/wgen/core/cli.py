import os
import sys
import time
from zipfile import (
    ZipFile,
    ZIP_DEFLATED,
    ZIP_BZIP2,
    ZIP_LZMA
)
from itertools import product, islice
from multiprocessing import Pool
from rich import print
from rich.progress import Progress
from typing import Literal
from .base import (
    human_readable,
    gen_chunk,
    estimate_file_size,
    get_pbar
)

ZIPMethod = Literal['normal', 'bzip2', 'lzma']

def wordlist_generator(chrs: str, min_length: int, max_length: int, zip_method: ZIPMethod, output: str, processes: int) -> None:
    if min_length > max_length:
        print('[bold red][!][/] [bold cyan]`min_length`[/] must be smaller or same as [bold cyan]`max_length`[/]')
        sys.exit(1)

    if zip_method == 'normal':
        compression = ZIP_DEFLATED
    elif zip_method == 'bzip2':
        compression = ZIP_BZIP2
    elif zip_method == 'lzma':
        compression = ZIP_LZMA

    if not output.lower().endswith('.zip'):
        zip_output = os.path.splitext(output)[0] + '.zip'
    else:
        zip_output = output
    txt_filename = os.path.splitext(os.path.basename(zip_output))[0] + '.txt'
    os.makedirs(os.path.dirname(zip_output) or '.', exist_ok=True)
    total_passwords = sum(len(chrs) ** i for i in range(min_length, max_length + 1))
    file_size = estimate_file_size(chrs, min_length, max_length)

    print(
        f'[bold blue][I][/] Output file: [bold cyan]`{zip_output}`[/]\n'
        f'[bold blue][I][/] [bold red]{total_passwords:,}[/] passwords will be generated\n'
        f'[bold blue][I][/] Estimated file size: [bold magenta]{human_readable(file_size)}[/]'
    )

    start_time = time.time()
    try:
        with ZipFile(zip_output, 'w', compression=compression, compresslevel=9) as zf:
            with zf.open(txt_filename, 'w') as outfile, Progress(*get_pbar(), transient=True) as progress:
                task_id = progress.add_task(
                    '[bold green][+][/]',
                    total=total_passwords
                )

                if processes == 1:
                    _generate_single_process(chrs, min_length, max_length, outfile, progress, task_id)
                else:
                    _generate_multi_process(chrs, min_length, max_length, outfile, progress, task_id, processes)
        end_time = time.time()
        actual_size = os.path.getsize(zip_output)

        print(
            f'[bold green][+][/] Wordlist generate completed!\n'
            f'[bold blue][I][/] ZIP file size: [bold magenta]{human_readable(actual_size)}[/]\n'
            f'[bold blue][I][/] Time taken: [bold red]{end_time - start_time:.2f}s[/]\n'
            f'[bold blue][I][/] Compression rate: [bold green]{(1 - actual_size / file_size) * 100:.2f}%[/]'
        )

    except Exception as e:
        print(f'[bold red][!][/] Error during generation: {str(e)}')
        if os.path.exists(zip_output):
            try:
                os.remove(zip_output)
                print(f'[bold yellow][!][/] Removed incomplete files: {zip_output}')
            except:
                pass
        sys.exit(1)

def _generate_single_process(chrs: str, min_length: int, max_length: int, outfile, progress, task_id):
    try:
        import psutil
        mem = psutil.virtual_memory()
        password_size = max(len(chrs), 8) * 8
        batch_size = max(50000, min(500000, int(mem.available * 0.3 / password_size)))
    except ImportError:
        batch_size = 100000

    for length in range(min_length, max_length + 1):
        passwords = product(chrs, repeat=length)

        while True:
            chunk = list(islice(passwords, batch_size))
            if not chunk:
                break

            data = ''.join(''.join(password) + '\n' for password in chunk)
            outfile.write(data.encode('utf-8'))
            progress.update(task_id, advance=len(chunk))
            del chunk, data

def _generate_multi_process(chrs: str, min_length: int, max_length: int, outfile, progress, task_id, processes: int):
    for length in range(min_length, max_length + 1):
        total = len(chrs) ** length

        base_chunk_size = min(100000, total // (processes * 4))
        max_chunk_size = 500000
        chunk_size = min(base_chunk_size, max_chunk_size)

        if chunk_size == 0:
            chunk_size = total
        args_list = []
        start_idx = 0

        while start_idx < total:
            end_idx = min(start_idx + chunk_size, total)
            args_list.append((chrs, length, start_idx, end_idx))
            start_idx = end_idx

        with Pool(processes=processes) as pool:
            for chunk_data in pool.imap(gen_chunk, args_list, chunksize=1):
                if chunk_data:
                    outfile.write(chunk_data.encode('utf-8'))
                    chunk_count = chunk_data.count('\n')
                    progress.update(task_id, advance=chunk_count)
