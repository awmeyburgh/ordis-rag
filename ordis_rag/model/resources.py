from typing import List
from pydantic import BaseModel, Field


class Resources(BaseModel):
    uniqueNames: List[str] = Field(
        description="List of the uniqueNames of required resources"
    )