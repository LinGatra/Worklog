import re
import unicodedata
from dataclasses import dataclass

from app.exception_handling.domain_exceptions import DomainValidationException

blacklist = {'Cc', 'Cf', 'Cs', 'Co'}
_WHITESPACE_RE = re.compile(r'\s')


@dataclass(frozen=True)
class FieldPolicy:
    letters: set[str]
    punctuation: set[str]
    digits: set[str]
    separators: set[str]
    symbols: set[str]
    min_length: int
    max_length: int


allowed_unicode_categories = {
    'letters': {'Lu', 'Ll'},
    'numbers': {'Nd', 'No'},
    'punctuation': {'Pc', 'Pd', 'Ps', 'Pe', 'Pi', 'Pf', 'Po'},
    'symbols': {'Sm', 'Sc', 'Sk'},
    'separators': {'Zs'},
}

en_lower = 'abcdefghijklmnopqrstuvwxyz'
ru_lower = 'абвгдеёжзийклмнопрстуфхцчшщьыъэюя'

digits = set('0123456789')

allowed_alias_symbols = set(en_lower + ru_lower) | digits

CLIENT_NAME_POLICY = FieldPolicy(
    letters=allowed_unicode_categories['letters'],
    punctuation=allowed_unicode_categories['punctuation'],
    digits=allowed_unicode_categories['numbers'],
    separators=allowed_unicode_categories['separators'],
    symbols=allowed_unicode_categories['symbols'],
    min_length=1,
    max_length=100,
)

SERVICE_NAME_POLICY = FieldPolicy(
    letters=allowed_unicode_categories['letters'],
    punctuation=allowed_unicode_categories['punctuation'],
    digits=allowed_unicode_categories['numbers'],
    separators=allowed_unicode_categories['separators'],
    symbols=allowed_unicode_categories['symbols'],
    min_length=1,
    max_length=100,
)

_POLICIES = {
    'client_name': CLIENT_NAME_POLICY,
    'offering_name': SERVICE_NAME_POLICY,
}

_COMPILED = {
    field_name: policy.letters
    | policy.punctuation
    | policy.digits
    | policy.separators
    | policy.symbols
    for field_name, policy in _POLICIES.items()
}

# упрощённая версия 'ISO 9'
_CYR_TO_LAT = str.maketrans(
    {
        'а': 'a',
        'б': 'b',
        'в': 'v',
        'г': 'g',
        'д': 'd',
        'е': 'e',
        'ё': 'e',
        'ж': 'zh',
        'з': 'z',
        'и': 'i',
        'й': 'y',
        'к': 'k',
        'л': 'l',
        'м': 'm',
        'н': 'n',
        'о': 'o',
        'п': 'p',
        'р': 'r',
        'с': 's',
        'т': 't',
        'у': 'u',
        'ф': 'f',
        'х': 'h',
        'ц': 'c',
        'ч': 'ch',
        'ш': 'sh',
        'щ': 'sch',
        'ъ': '',
        'ы': 'y',
        'ь': '',
        'э': 'e',
        'ю': 'yu',
        'я': 'ya',
    }
)


def sanitize(str_in: str) -> str:
    if not isinstance(str_in, str):
        raise TypeError
    if not str_in:
        raise TypeError

    normalized_whitespace = _WHITESPACE_RE.sub(' ', str_in)
    data = ''.join(
        char for char in normalized_whitespace if unicodedata.category(char) not in blacklist
    )
    if not data:
        raise DomainValidationException
    return data


def normalize_for_ui(str_in: str, field_name: str) -> str:
    if not (isinstance(str_in, str) and isinstance(field_name, str)):
        raise TypeError
    if not (str_in and field_name):
        raise TypeError

    sanitized_string = sanitize(str_in=str_in)
    try:
        allowed = _COMPILED[field_name]

        data = ' '.join(sanitized_string.split())
        data = unicodedata.normalize('NFC', data)

        if not data:
            raise DomainValidationException
        for char in data:
            if unicodedata.category(char) not in allowed:
                raise DomainValidationException
        return data
    except KeyError as e:
        raise ValueError from e


def make_alias(str_in: str, field_name: str) -> str:
    if not (isinstance(str_in, str) and isinstance(field_name, str)):
        raise TypeError
    if not (str_in and field_name):
        raise TypeError

    data = normalize_for_ui(str_in=str_in, field_name=field_name)
    data = data.casefold().translate(_CYR_TO_LAT)
    data = unicodedata.normalize('NFKD', data)

    alias = ''.join(char for char in data if char in allowed_alias_symbols)
    if not alias:
        raise DomainValidationException
    return alias


def validate(normalized_str: str, field_name: str) -> bool:
    if not (isinstance(normalized_str, str) and isinstance(field_name, str)):
        raise TypeError
    if not (normalized_str and field_name):
        raise TypeError
    try:
        min_length = _POLICIES[field_name].min_length
        max_length = _POLICIES[field_name].max_length

        if not (min_length <= len(normalized_str) <= max_length):
            raise DomainValidationException
    except KeyError as e:
        raise ValueError from e

    return True


if __name__ == '__main__':
    print(sorted(_COMPILED.items()))
    print('=' * 50)
    print(allowed_alias_symbols)
