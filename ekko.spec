# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Ekko — local-only Windows EXE (onedir)."""

import os
from pathlib import Path

block_cipher = None

ROOT = Path(SPECPATH)
BACKEND = ROOT / "backend"
SRC = BACKEND / "src"
PKG = SRC / "ekko"

datas = [
    # AI prompts
    (str(PKG / "ai" / "prompts"), os.path.join("ekko", "ai", "prompts")),
    # Built frontend (produced by `bun run build` before PyInstaller)
    (str(ROOT / "frontend" / "dist"), "frontend"),
]
binaries = []
hiddenimports = [
    # Uvicorn internals
    "uvicorn.logging",
    "uvicorn.lifespan.on",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.protocols.websockets.wsproto_impl",
    # SQLAlchemy dialects
    "sqlalchemy.dialects.sqlite",
    "aiosqlite",
    # Ekko submodules
    "ekko.composition.app_factory",
    "ekko.config.settings",
    "ekko.config.settings.base",
    "ekko.config.settings.local",
    "ekko.config.settings.test_env",
    "ekko.infrastructure.db",
    "ekko.infrastructure.db.base",
    "ekko.infrastructure.db.models",
    "ekko.presentation.api.routes",
    "ekko.presentation.graphql.router",
    # Strawberry GraphQL
    "strawberry",
    "strawberry.fastapi",
    # Pydantic
    "pydantic",
    "pydantic_settings",
]

a = Analysis(
    [str(BACKEND / "src" / "ekko" / "cli" / "run_app.py")],
    pathex=[str(SRC)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "playwright",
        "storybook",
        "gunicorn",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ekko",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="ekko",
)
