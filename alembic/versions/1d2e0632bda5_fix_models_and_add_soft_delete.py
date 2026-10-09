"""fix_models_and_add_soft_delete

Revision ID: 1d2e0632bda5
Revises: ea18c0067a1a
Create Date: 2026-09-03 05:59:41.168029

"""

import re
import unicodedata
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '1d2e0632bda5'
down_revision: str | Sequence[str] | None = 'ea18c0067a1a'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

__blacklist = {'Cc', 'Cf', 'Cs', 'Co'}
__WHITESPACE_RE = re.compile(r'\s')


__COMPILED_SNAPSHOT = {
    'client_name': {
        'Pc',
        'Po',
        'Lu',
        'Ps',
        'Pi',
        'Pd',
        'Pe',
        'Nd',
        'Pf',
        'No',
        'Sm',
        'Zs',
        'Sc',
        'Ll',
        'Sk',
    },
    'offering_name': {
        'Pc',
        'Po',
        'Lu',
        'Ps',
        'Pi',
        'Pd',
        'Pe',
        'Nd',
        'Pf',
        'No',
        'Sm',
        'Zs',
        'Sc',
        'Ll',
        'Sk',
    },
}

__allowed_alias_symbols_snapshot = {
    '3',
    '2',
    'h',
    'w',
    '0',
    'x',
    'l',
    'у',
    '1',
    'х',
    'ж',
    'з',
    'ш',
    'т',
    'z',
    '6',
    't',
    'э',
    'ф',
    'щ',
    'u',
    'й',
    'м',
    'ъ',
    '4',
    '5',
    'i',
    '7',
    '9',
    'н',
    'и',
    'я',
    'ь',
    'q',
    'д',
    'ы',
    'g',
    'п',
    'с',
    'b',
    'е',
    'к',
    '8',
    'm',
    'n',
    'ё',
    'г',
    'k',
    'ч',
    'y',
    'r',
    'ц',
    'ю',
    'e',
    'p',
    'б',
    's',
    'j',
    'd',
    'о',
    'a',
    'c',
    'o',
    'р',
    'v',
    'в',
    'а',
    'л',
    'f',
}

__CYR_TO_LAT = str.maketrans(
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

__en_lower = 'abcdefghijklmnopqrstuvwxyz'

__digits = set('0123456789')

__allowed_alias_symbols = set(__en_lower) | __digits


class DomainValidationException(Exception):
    pass


def __sanitize_snapshot(str_in: str) -> str:
    if not isinstance(str_in, str):
        raise TypeError
    if not str_in:
        raise TypeError

    normalized_whitespace = __WHITESPACE_RE.sub(' ', str_in)
    data = ''.join(
        char for char in normalized_whitespace if unicodedata.category(char) not in __blacklist
    )
    if not data:
        raise DomainValidationException
    return data


def __normalize_for_ui_snapshot(str_in: str, field_name: str) -> str:
    if not (isinstance(str_in, str) and isinstance(field_name, str)):
        raise TypeError
    if not (str_in and field_name):
        raise ValueError

    sanitized_string = __sanitize_snapshot(str_in=str_in)
    allowed = __COMPILED_SNAPSHOT[field_name]
    data = unicodedata.normalize('NFC', sanitized_string)

    if not data:
        raise DomainValidationException
    for char in data:
        if unicodedata.category(char) not in allowed:
            raise DomainValidationException
    return data


def __make_alias_snapshot(str_in: str, field_name: str) -> str:
    if not (isinstance(str_in, str) and isinstance(field_name, str)):
        raise TypeError
    if not (str_in and field_name):
        raise TypeError

    data = __normalize_for_ui_snapshot(str_in=str_in, field_name=field_name)
    data = data.casefold().translate(__CYR_TO_LAT)
    data = unicodedata.normalize('NFKD', data)

    alias = ''.join(char for char in data if char in __allowed_alias_symbols)
    if not alias:
        raise DomainValidationException
    return alias


client_current = sa.table(
    'client',
    sa.column('client_id', sa.Integer),
    sa.column('client_name', sa.String),
)

offering_current = sa.table(
    'offering',
    sa.column('offering_id', sa.Integer),
    sa.column('offering_name', sa.String),
)

client_new = sa.table(
    'client',
    sa.column('client_id', sa.Integer),
    sa.column('client_name', sa.String),
    sa.column('name_alias', sa.String),
    sa.column('is_deleted', sa.Boolean),
)

offering_new = sa.table(
    'offering',
    sa.column('offering_id', sa.Integer),
    sa.column('offering_name', sa.String),
    sa.column('name_alias', sa.String),
    sa.column('is_deleted', sa.Boolean),
)


def get_data(bind: sa.Connection, table: sa.TableClause):
    table_columns = [column for column in table.columns]

    rows = bind.execute(sa.select(*table_columns)).fetchall()
    return rows


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()

    # get current `client` data
    rows = get_data(bind=bind, table=client_current)

    # transform `client` table
    op.add_column('client', sa.Column('name_alias', sa.String(), nullable=True))
    op.add_column(
        'client', sa.Column('is_deleted', sa.Boolean(), nullable=True, server_default=sa.false())
    )

    # normalize `.client_name` and create `.name_alias`
    for row in rows:
        new_client_name = __normalize_for_ui_snapshot(
            str_in=row.client_name, field_name='client_name'
        )
        new_name_alias = __make_alias_snapshot(str_in=new_client_name, field_name='client_name')

        bind.execute(
            sa.update(client_new)
            .where(client_new.columns.client_id == row.client_id)
            .values(
                client_name=new_client_name,
                name_alias=new_name_alias,
            )
        )

    # get current `offering` data
    rows = get_data(bind=bind, table=offering_current)

    # transform `offering` table
    op.add_column('offering', sa.Column('name_alias', sa.String(), nullable=True))
    op.add_column(
        'offering', sa.Column('is_deleted', sa.Boolean(), nullable=True, server_default=sa.false())
    )

    # normalize `.offering_name` and create `.name_alias`
    for row in rows:
        new_offering_name = __normalize_for_ui_snapshot(
            str_in=row.offering_name, field_name='offering_name'
        )
        new_name_alias = __make_alias_snapshot(str_in=new_offering_name, field_name='offering_name')

        bind.execute(
            sa.update(offering_new)
            .where(offering_new.columns.offering_id == row.offering_id)
            .values(
                offering_name=new_offering_name,
                name_alias=new_name_alias,
            )
        )

    # froze tables
    op.alter_column('client', 'name_alias', nullable=False)
    op.alter_column('client', 'is_deleted', nullable=False)
    op.alter_column('offering', 'name_alias', nullable=False)
    op.alter_column('offering', 'is_deleted', nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('offering', 'is_deleted')
    op.drop_column('offering', 'name_alias')
    op.drop_column('client', 'is_deleted')
    op.drop_column('client', 'name_alias')
    # ### end Alembic commands ###
