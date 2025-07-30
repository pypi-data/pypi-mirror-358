from abc import ABC
from ..config.config import ConfigProducteca
from dataclasses import dataclass
from typing import Optional


@dataclass
class BaseService[T](ABC):
    config: ConfigProducteca
    endpoint: str
    _record: Optional[T] = None