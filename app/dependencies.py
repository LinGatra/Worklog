import asyncio
import re
import unicodedata

from fastapi import Request


async def db_connect(request: Request):
    async_session_factory = request.app.state.session_factory
    async with async_session_factory() as session:
        yield session


async def _create_translit_table():
    rules = {
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
        'х': 'kh',
        'ц': 'ts',
        'ч': 'ch',
        'ш': 'sh',
        'щ': 'shch',
        'ы': 'y',
        'э': 'e',
        'ю': 'yu',
        'я': 'ya',
        'ъ': '',
        'ь': '',
    }
    return str.maketrans(rules)


TRANSLIT_TABLE = asyncio.run(_create_translit_table())


async def create_alias(data: str) -> str:
    data = unicodedata.normalize('NFKD', data)
    data = data.lower().strip()
    data = data.translate(TRANSLIT_TABLE)
    data = re.sub(r'[^a-z0-9]', '', data)

    return data
