from enum import nonmember
import json
from pprint import pprint
from pydantic import BaseModel, ValidationError
from typing import ClassVar, List, Optional, Dict
from datetime import datetime, date
import json

from ordis_rag.resource.stats.base_stats import BaseStats

class Patchlog(BaseModel):
    name: str
    date: datetime
    url: str
    additions: str
    changes: str
    fixes: str

class Ability(BaseModel):
    uniqueName: str

class Component(BaseModel):
    uniqueName: str

class Introduced(BaseModel):
    name: str
    url: str
    aliases: List[str]
    parent: str
    date: date

class Warframe(BaseStats):
    description: Optional[str] = None
    type: Optional[str] = None
    tradable: Optional[bool] = None
    productCategory: Optional[str] = None
    patchlogs: Optional[List[Patchlog]] = None
    components: Optional[List[Component]] = None
    introduced: Optional[Introduced] = None
    estimatedVaultDate: Optional[date] = None
    shield: Optional[int] = None
    polarities: Optional[List[str]] = None
    prime_power: Optional[str] = None
    prime_mr: Optional[str] = None
    color: Optional[int] = None
    prime_polarities: Optional[List[str]] = None
    conclave: Optional[bool] = None
    prime_armor: Optional[int] = None
    speed: Optional[str] = None
    aura: Optional[str] = None
    prime_url: Optional[str] = None
    prime_health: Optional[int] = None
    power: Optional[int] = None
    prime_aura: Optional[str] = None
    info: Optional[str] = None
    thumbnail: Optional[str] = None
    mr: Optional[str] = None
    prime_shield: Optional[int] = None
    health: Optional[int] = None
    prime_speed: Optional[str] = None
    url: Optional[str] = None
    regex: Optional[str] = None
    armor: Optional[int] = None
    location: Optional[str] = None
    prime_conclave: Optional[str] = None
    abilities: Optional[List[Ability]] = None
    buildPrice: Optional[int] = None
    buildQuantity: Optional[int] = None
    buildTime: Optional[int] = None
    consumeOnBuild: Optional[bool] = None
    isPrime: Optional[bool] = None
    masterable: Optional[bool] = None
    masteryReq: Optional[int] = None
    releaseDate: Optional[str] = None
    skipBuildTimePrice: Optional[int] = None
    sprint: Optional[float] = None
    sprintSpeed: Optional[float] = None
    stamina: Optional[int] = None

    @classmethod
    def load_all(cls) -> Dict[str, "Warframe"]:
        with open("data/stats/warframes.json", 'r') as f:
            data = json.load(f)
        result = {}
        for warframe_data in data:
            try:
                result[warframe_data['uniqueName']] = cls(**warframe_data)
            except ValidationError as exc:
                print(repr(exc.errors()[0]['loc']))
                raise exc
        return result