import pytest

from app.exception_handling.domain_exceptions import DomainValidationException
from app.limitations import make_alias, normalize_for_ui, sanitize

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        ('hello world', 'hello world'),
        ('hello   world', 'hello world'),
        ('hello\tworld\n', 'hello world'),
        ('  hello world  ', 'hello world'),
    ],
)
async def test_sanitize_transform_strings(value, expected):
    sanitized_text = sanitize(str_in=value)
    assert sanitized_text == expected


async def test_sanitize_handles_incorrect_input():
    with pytest.raises(DomainValidationException):
        sanitize('\t')


async def test_normalize_for_ui_raises_key_error_on_unknown_field_name():
    with pytest.raises(KeyError):
        normalize_for_ui(str_in='Correct String', field_name='Incorrect field')


@pytest.mark.parametrize(
    argnames=('str_in', 'field_name'), argvalues=[('Correct Name', ''), ('', 'client_name')]
)
async def test_normalize_for_ui_raises_value_error_on_empty_parameter(str_in, field_name):
    with pytest.raises(ValueError):
        normalize_for_ui(str_in=str_in, field_name=field_name)


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        ('транслитерация', 'transliteraciya'),
        ('\t    remove white spaces    \n', 'removewhitespaces'),
        ('CASEFOLD', 'casefold'),
        ('Remove Symbols_!%^&%$', 'removesymbols'),
    ],
)
async def test_make_alias(value, expected):
    normalized_text = make_alias(str_in=value, field_name='client_name')
    assert normalized_text == expected


async def test_make_alias_raises_domain_validation_exception_on_incorrect_input():
    with pytest.raises(DomainValidationException):
        make_alias(str_in='\t', field_name='client_name')


async def test_make_alias_raises_key_error_on_unknown_field_name():
    with pytest.raises(KeyError):
        make_alias(str_in='Correct String', field_name='Incorrect field')
