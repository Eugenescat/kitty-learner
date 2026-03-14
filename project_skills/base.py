"""Minimal skill abstraction for project capabilities."""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class Skill(ABC):
    """Base class for a reusable capability module."""

    name: str
    input_schema: type[BaseModel] | None = None
    output_schema: type[BaseModel] | None = None

    @abstractmethod
    def run(self, **kwargs: Any) -> Any:
        """Execute the skill with keyword args."""

