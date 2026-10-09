from typing import Annotated

from pydantic import Field

LimitedIntID = Annotated[int, Field(ge=0, le=1_000_000)]

ClientName = Annotated[
    str,
    Field(
        min_length=1,
        max_length=100,
        description='Only latin, cyrillic, numeric and punctuation symbols.',
    ),
]

OfferingName = Annotated[
    str,
    Field(
        min_length=1,
        max_length=100,
        description='Only latin, cyrillic, numeric and punctuation symbols.',
    ),
]

AltPrice = Annotated[
    int, Field(ge=0, lt=1_000_000, description='Price must be in range between 0 and 1.000.000')
]

OfferingPrice = Annotated[
    int, Field(ge=0, le=1_000_000, description='Price must be in range between 0 and 1.000.000')
]
