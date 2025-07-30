import string

CHARSET_DICT = {
    '0': string.digits,
    'a': string.ascii_lowercase,
    'A': string.ascii_uppercase,
    '@': string.punctuation
}

def charset2string(chars: str, string_added: str | None=None) -> str:
    charset = ''
    for key, value in CHARSET_DICT.items():
        for i in range(len(chars)):
            if chars[i] == key:
                charset += value
    if string_added:
        charset += string_added
    return charset
