import unicodedata
from dataclasses import dataclass

from app.exception_handling.domain_exceptions import DomainValidationException

blacklist = {'Cc', 'Cf', 'Cs', 'Co'}


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
    'symbols': {'Sm', 'Sc', 'Sk', 'So'},
    'separators': {'Zs'},
}

en_lower = 'abcdefghijklmnopqrstuvwxyz'

digits = set('0123456789')

allowed_alias_symbols = set(en_lower) | digits

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

    # Filters out prohibited Unicode categories and collapses whitespace characters into a single space.
    data = ' '.join(
        ''.join(char for char in word if unicodedata.category(char) not in blacklist)
        for word in str_in.split()
    )

    if not data:
        raise DomainValidationException
    return data


def normalize_for_ui(str_in: str, field_name: str) -> str:
    if not (isinstance(str_in, str) and isinstance(field_name, str)):
        raise TypeError
    if not (str_in and field_name):
        raise ValueError
    if field_name not in _POLICIES:
        raise KeyError

    sanitized_string = sanitize(str_in=str_in)
    allowed = _COMPILED[field_name]
    data = unicodedata.normalize('NFC', sanitized_string)

    if not data:
        raise DomainValidationException
    for char in data:
        if unicodedata.category(char) not in allowed:
            raise DomainValidationException
    return data


def make_alias(str_in: str, field_name: str) -> str:
    if not (isinstance(str_in, str) and isinstance(field_name, str)):
        raise TypeError
    if not (str_in and field_name):
        raise TypeError
    if field_name not in _POLICIES:
        raise KeyError

    data = normalize_for_ui(str_in=str_in, field_name=field_name)
    data = data.casefold().translate(_CYR_TO_LAT)
    data = unicodedata.normalize('NFKD', data)

    alias = ''.join(char for char in data if char in allowed_alias_symbols)
    if not alias:
        raise DomainValidationException
    return alias


if __name__ == '__main__':
    print(sorted(_COMPILED.items()))
    print('=' * 50)
    print(allowed_alias_symbols)
