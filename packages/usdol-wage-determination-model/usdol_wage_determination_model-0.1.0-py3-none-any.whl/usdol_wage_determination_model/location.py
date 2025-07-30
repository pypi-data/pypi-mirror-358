from pydantic import BaseModel


class Location(BaseModel):
    state: str
    county: str
