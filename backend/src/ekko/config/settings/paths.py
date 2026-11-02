"""Filesystem path settings derived from the repository root."""

from __future__ import annotations

from pathlib import Path

from ekko.config.runtime import ROOT_DIR_PATH
from ekko.config.settings._shared import ConfiguredSettings


class PathSettings(ConfiguredSettings):
    """Filesystem paths derived from the repository root."""

    root_dir_path: Path = ROOT_DIR_PATH
    src_dir_path: Path = root_dir_path / "src"
    package_dir_path: Path = src_dir_path / "ekko"
    logs_dir_path: Path = root_dir_path / "logs"
    prompt_dir_path: Path = package_dir_path / "ai" / "prompts"
