import json
from typing import Any, Dict, Optional

from pydantic import ValidationError

from ordis_rag.resource.stats.base_stats import BaseStats
from ordis_rag.resource.stats.warframe import Warframe


class Stats:
    __ALL_RESOURCES: Optional[Dict[str, str]] = None

    @classmethod
    def all_resources(cls) -> Dict[str, str]:
        if cls.__ALL_RESOURCES is None:
            cls.__ALL_RESOURCES = {}
            
            for uniqueName, model in cls.all().items():
                cls.__ALL_RESOURCES[uniqueName] = f'{model.uniqueName}:::{model.category}:::{model.name}'

        return cls.__ALL_RESOURCES

    __ALL: Optional[Dict[str, BaseStats]] = None

    @classmethod
    def load_stats(cls, filename) -> Dict[str, BaseStats]:
        with open(f"data/stats/{filename}", 'r') as f:
            data = json.load(f)
        result = {}
        for warframe_data in data:
            try:
                result[warframe_data['uniqueName']] = BaseStats(**warframe_data)
            except ValidationError as exc:
                print(repr(exc.errors()[0]['loc']))
                raise exc
        return result

    @classmethod
    def all(cls) -> Dict[str, BaseStats]:
        if cls.__ALL is None:
            cls.__ALL = {}
            for filename in ['warframes.json', 'weapons.json', 'mods.json']:
                for uniqueName, model in cls.load_stats(filename).items():
                    cls.__ALL[uniqueName] = model
        return cls.__ALL