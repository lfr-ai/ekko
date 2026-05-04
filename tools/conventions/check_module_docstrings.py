"""Check that every Python module has a module-level docstring.

Scans ``backend/src/ekko/`` and reports files missing a module docstring.
Run locally or in CI to enforce documentation standards.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "backend" / "src" / "ekko"


def _has_module_docstring(path: Path) -> bool:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return True  # skip unparsable files
    return ast.get_docstring(tree) is not None


def main() -> int:
    """Report modules missing docstrings.

    Returns:
        Process exit code (1 if violations found, 0 otherwise).
    """
    missing: list[Path] = []
    for py in sorted(SRC.rglob("*.py")):
        if py.name == "__init__.py":
            continue
        if not _has_module_docstring(py):
            missing.append(py.relative_to(ROOT))

    if not missing:
        print("All modules have docstrings.")
        return 0

    print(f"Missing module docstrings ({len(missing)} files):\n")
    for p in missing:
        print(f"  {p}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
