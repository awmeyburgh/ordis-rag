from typing import Literal
from pydantic import BaseModel, Field


class Grade(BaseModel):
    relevant: bool = Field(
        description="Whether this document is relevant to question"
    )