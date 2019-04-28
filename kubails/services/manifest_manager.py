import logging
import os
import yaml
from typing import Any, Dict


logger = logging.getLogger(__name__)


class ManifestManager:
    def __init__(self, manifests_folder="manifests", static_folder="static", generated_folder="generated"):
        self.manifests_folder = manifests_folder
        self.static_folder = static_folder
        self.generated_folder = generated_folder

    def load_static_manifest(self, manifest_location: str) -> Dict[str, Any]:
        return self.load_manifest(self.static_manifest_location(manifest_location))

    def load_manifest(self, manifest_location: str) -> Dict[str, Any]:
        with open(manifest_location, "r") as f:
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError as e:
                logger.exception(str(e))
                return None

    def write_static_manifest(self, manifest: Dict[str, Any], manifest_location: str) -> bool:
        return self.write_manifest(manifest, self.static_manifest_location(manifest_location))

    def write_manifest(self, manifest: Dict[str, Any], manifest_location: str) -> bool:
        with open(manifest_location, "w") as f:
            try:
                yaml.dump(manifest, f, Dumper=IgnoreAliasesDumper, default_flow_style=False, explicit_start=True)
                return True
            except yaml.YAMLError as e:
                logger.exception(str(e))
                return False

    def static_manifest_location(self, manifest_location: str) -> str:
        return os.path.join(self.manifests_folder, self.static_folder, manifest_location)

    def generated_manifest_location(self, manifest_location: str) -> str:
        return os.path.join(self.manifests_folder, self.generated_folder, manifest_location)


class IgnoreAliasesDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True
