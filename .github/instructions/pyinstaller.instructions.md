---
description: PyInstaller spec-file conventions for reproducible executable builds
applyTo: "**/*.spec"
---

# PyInstaller spec files

- Treat the committed `.spec` as executable Python and the single source of truth
  for `Analysis`, data, hidden imports, binary mode, and signing inputs.
- Keep entry points thin, paths repository-relative, and `data`, `binaries`,
  `hiddenimports`, and `excludes` as named collections before `Analysis`.
- Never bundle `.env`, credentials, certificates, private keys, customer data, or
  host-specific absolute paths. Runtime configuration stays external.
- Prefer `onedir` for production startup, code signing, and antivirus inspection;
  choose `onefile` only for a verified distribution requirement.
- Build independently on every target OS; PyInstaller is not a cross-compiler.
  Validate the artifact on a clean machine without Python installed.
- Follow the `pyinstaller` skill and run the project-owned package task after
  every spec or bundled-resource change.
