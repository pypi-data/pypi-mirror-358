from typing import Dict, Any

class HistoryArtifactCompatible:

    def to_text(self) -> str:
        pass

    @classmethod
    def from_text(cls, payload: str) -> Any:
        pass
