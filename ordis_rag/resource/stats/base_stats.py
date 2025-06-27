from enum import nonmember
from typing import Optional
from pydantic import BaseModel


class BaseStats(BaseModel):
    name: str
    uniqueName: str
    category: str
    wikiAvailable: Optional[bool] = None
    wikiaThumbnail: Optional[str] = None
    wikiaUrl: Optional[str] = None