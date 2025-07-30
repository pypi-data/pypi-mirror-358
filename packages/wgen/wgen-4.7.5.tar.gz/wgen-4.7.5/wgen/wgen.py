from argparse import (
    ArgumentParser,
    RawTextHelpFormatter
)
from core import (
    BANNER,
    DEFAULT_CHAR,
    charset2string,
    wordlist_generator,
    CHAR_HELP,
    STRING_ADDED_HELP,
    MIN_LENGTH_HELP,
    MAX_LENGTH_HELP,
    COMPRESS_METHOD_HELP,
    OUTPUT_HELP,
    PROCESSES_HELP
)

def main():
    parser = ArgumentParser(formatter_class=RawTextHelpFormatter, description=BANNER)
    parser.add_argument('-c', '--chars', type=str, default=DEFAULT_CHAR, help=CHAR_HELP)
    parser.add_argument('-add', '--string-added', type=str, default=None, help=STRING_ADDED_HELP)
    parser.add_argument('min', type=int, help=MIN_LENGTH_HELP)
    parser.add_argument('max', type=int, help=MAX_LENGTH_HELP)
    parser.add_argument('-m', '--method', type=str, default='lzma', help=COMPRESS_METHOD_HELP)
    parser.add_argument('-o', '--output', type=str, default='./wordlists.txt', help=OUTPUT_HELP)
    parser.add_argument('-p', '--processes', type=int, default=5, help=PROCESSES_HELP)
    args = parser.parse_args()
    chars = charset2string(args.chars, args.string_added)
    wordlist_generator(chars, args.min, args.max, args.method, args.output, args.processes)

if __name__ == '__main__':
    main()
