from __future__ import annotations

from pathlib import Path
from typing import Any
import json


class RegistryError(Exception):
    pass


class Registry:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.capabilities: dict[str, dict[str, Any]] = {}
        self.workflows: dict[str, dict[str, Any]] = {}

    def load_json(self, path: str | Path) -> dict[str, Any]:
        return json.loads(Path(path).read_text(encoding="utf-8"))

    def register_capability(self, manifest: dict[str, Any]) -> None:
        if manifest.get("apiVersion") != "a1os/v1" or manifest.get("kind") != "Capability":
            raise RegistryError("Invalid capability manifest")
        identifier = manifest["metadata"]["id"]
        self.capabilities[identifier] = manifest

    def register_workflow(self, manifest: dict[str, Any]) -> None:
        if manifest.get("apiVersion") != "a1os/v1" or manifest.get("kind") != "Workflow":
            raise RegistryError("Invalid workflow manifest")
        identifier = manifest["metadata"]["id"]
        capability = manifest["spec"]["capability"]["id"]
        if capability not in self.capabilities:
            raise RegistryError(f"Unknown capability: {capability}")
        self.workflows[identifier] = manifest

    def discover(self) -> None:
        for path in sorted(self.root.rglob("*.json")):
            if path.name.endswith(".schema.json"):
                continue
            data = self.load_json(path)
            kind = data.get("kind")
            if kind == "Capability":
                self.register_capability(data)
            elif kind == "Workflow":
                self.register_workflow(data)

    def get_capability(self, identifier: str) -> dict[str, Any]:
        try:
            return self.capabilities[identifier]
        except KeyError as exc:
            raise RegistryError(f"Capability not registered: {identifier}") from exc

    def get_workflow(self, identifier: str) -> dict[str, Any]:
        try:
            return self.workflows[identifier]
        except KeyError as exc:
            raise RegistryError(f"Workflow not registered: {identifier}") from exc

    def plan(self, workflow_id: str) -> dict[str, Any]:
        workflow = self.get_workflow(workflow_id)
        capability = self.get_capability(workflow["spec"]["capability"]["id"])
        return {
            "workflow": workflow_id,
            "capability": capability["metadata"]["id"],
            "dependencies": capability["spec"].get("dependencies", []),
            "prerequisites": workflow["spec"].get("prerequisites", []),
            "stages": workflow["spec"].get("stages", []),
            "verification": workflow["spec"].get("verification", []),
            "destructive": workflow["spec"].get("destructive", False),
        }
