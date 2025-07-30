from pydantic import BaseModel


class Job(BaseModel):
    title: str
    category: str
    classification: str
