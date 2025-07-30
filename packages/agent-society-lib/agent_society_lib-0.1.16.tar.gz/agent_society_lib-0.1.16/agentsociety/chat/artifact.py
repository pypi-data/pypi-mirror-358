from typing import Dict, List
from dataclasses import dataclass

@dataclass
class TaskArtifact:
    artifact_name: str
    content: str

    def to_json(self) -> Dict[str, str]:
        return {
            "artifact_name": self.artifact_name,
            "content": self.content
        }

@dataclass
class TaskArtifacts:
    results: List[TaskArtifact]
    
    def to_json(self) -> Dict[str, List[TaskArtifact]]:
        return {
        "results": [r.to_json() for r in self.results]
        }
