from pydantic import BaseModel, ConfigDict


class Config(BaseModel):
    model_config = ConfigDict(from_attributes=True)
