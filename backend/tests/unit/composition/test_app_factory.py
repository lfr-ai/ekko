"""Tests for application-factory composition helpers."""

from __future__ import annotations

import sys

import pytest
from fastapi import FastAPI
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from ekko.composition.app_factory import _mount_frontend


@pytest.mark.unit
def test_mount_frontend_when_frozen_uses_pyinstaller_resource_directory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    """Mount bundled frontend assets from PyInstaller's resource directory."""
    frontend_dir = tmp_path / "frontend"
    frontend_dir.mkdir()
    (frontend_dir / "index.html").write_text("<html>Ekko</html>", encoding="utf-8")
    app = FastAPI()

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)

    _mount_frontend(app)

    frontend_mount = next(route for route in app.routes if isinstance(route, Mount) and route.path == "")
    assert isinstance(frontend_mount.app, StaticFiles)
    assert frontend_mount.app.directory == str(frontend_dir)
