from pydantic import ConfigDict
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    model_config = ConfigDict(from_attributes=True)
