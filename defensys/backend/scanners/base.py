from abc import ABC, abstractmethod
from typing import List

class Scanner(ABC):
    @abstractmethod
    def scan(self, path: str) -> List[dict]:
        pass
