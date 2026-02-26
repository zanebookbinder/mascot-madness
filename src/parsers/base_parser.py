from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.bracket import Bracket


class BaseBracketParser(ABC):

    @abstractmethod
    def parse(self, source: str) -> "Bracket":
        """
        Parse a source and return a populated Bracket.

        Args:
            source: Implementation-defined source identifier (filepath, URL, etc.)

        Returns:
            A fully populated Bracket instance.

        Raises:
            ValueError: If source data is malformed or incomplete.
        """
        ...
