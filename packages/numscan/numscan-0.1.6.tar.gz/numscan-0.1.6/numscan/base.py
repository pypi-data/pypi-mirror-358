from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List


class NumberCounter(ABC):
    def __init__(self, filepath: str, limit: int = 1000) -> None:
        self.filepath: Path = Path(filepath)
        self.limit: int = limit
        self._numbers: List[int] = self._generate_numbers()
        self._counts: Dict[int, int] | None = None

    @property
    def counts(self) -> Dict[int, int]:
        if self._counts is None:
            self._counts = self._count_matches_in_file()
        return self._counts

    def refresh(self) -> None:
        self._counts = self._count_matches_in_file()

    @abstractmethod
    def _generate_numbers(self) -> List[int]:
        ...

    def _count_matches_in_file(self) -> Dict[int, int]:
        text = self.filepath.read_text(encoding="utf-8", errors="ignore")
        return {n: text.count(str(n)) for n in self._numbers}