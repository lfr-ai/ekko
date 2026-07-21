# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Ekko — local-only Windows EXE (onedir)."""

import os
from pathlib import Path

block_cipher = None

ROOT = Path(SPECPATH)
BACKEND = ROOT / "backend"
SRC = BACKEND / "src"
PKG = SRC / "ekko"

a = Analysis(
    [str(BACKEND / "src" / "ekko" / "cli" / "run_app.py")],
    pathex=[str(SRC)],
    binaries=[],
    data=[
        # AI prompts and CrewAI config
        (str(PKG / "ai" / "prompts"), os.path.join("ekko", "ai", "prompts")),
        (str(PKG / "ai" / "crewai" / "config"), os.path.join("ekko", "ai", "crewai", "config")),
        # Built frontend (produced by `bun run build` before PyInstaller)
        (str(ROOT / "frontend" / "dist"), "frontend"),
    ],
    hiddenimports=[
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
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "asyncpg",
        "psycopg2",
        "playwright",
        "storybook",
        "gunicorn",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Collect native DLLs for faster-whisper / ctranslate2
for pkg_name in ["faster_whisper", "ctranslate2", "numpy", "tiktoken"]:
    try:
        from PyInstaller.utils.hooks import collect_all
        pkg_data, pkg_binaries, pkg_hiddenimports = collect_all(pkg_name)
        a.data += pkg_data
        a.binaries += pkg_binaries
        a.hiddenimports += pkg_hiddenimports
    except Exception:
        pass

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
    a.data,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="ekko",
)
