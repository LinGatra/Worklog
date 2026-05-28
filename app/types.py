import re
import unicodedata
from typing import Annotated

from pydantic import BeforeValidator, Field


def sanitize_name(data: str) -> str:
    if not isinstance(data, str):
        raise TypeError("Name must be a 'str' type")

    allowed_types = {'Lu', 'Ll', 'Nd', 'Zs', 'Ps', 'Pe', 'Pi', 'Pf', 'Pd', 'Pc', 'Po'}
    data = unicodedata.normalize('NFKC', data)
    data = ''.join(char for char in data if unicodedata.category(char) in allowed_types)

    return re.sub(r'\s+', ' ', data).strip()


ClientName = Annotated[str, BeforeValidator(sanitize_name), Field(min_length=2, max_length=100)]
