import os
import tomllib
from pathlib import PurePath

from hatchling.metadata.plugin.interface import MetadataHookInterface


DEFAULT_VERSION = "0.0.0"
UV_LOCK = "uv.lock"


class CustomMetadataHook(MetadataHookInterface):
    def update(self, metadata: dict) -> None:
        script_dir = PurePath(os.path.dirname(os.path.realpath(__file__)))
        uv_lock_path = script_dir / UV_LOCK
        uv_lock = None

        if os.path.exists(uv_lock_path):
            with open(uv_lock_path, "rb") as uv_lock_f:
                uv_lock = tomllib.load(uv_lock_f)

        if not uv_lock:
            metadata["version"] = DEFAULT_VERSION
            return

        awscli_package = [ pkg for pkg in uv_lock["package"] if pkg.get("name") == "awscli" ]

        if not awscli_package:
            metadata["version"] = DEFAULT_VERSION
            return

        assert len(awscli_package) == 1, "Should only be one awscli package"
        metadata["version"] = awscli_package[0]["version"]
