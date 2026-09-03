"""Tests for database connection configuration callbacks."""

from unittest.mock import MagicMock

import pytest

from ekko.infrastructure.db import _set_sqlite_pragmas


@pytest.mark.unit
def test_set_sqlite_pragmas_when_execute_fails_closes_cursor() -> None:
    """SQLite connection setup closes its cursor when a PRAGMA fails."""
    cursor = MagicMock()
    cursor.execute.side_effect = RuntimeError("pragma failed")
    connection = MagicMock()
    connection.cursor.return_value = cursor

    with pytest.raises(RuntimeError, match="pragma failed"):
        _set_sqlite_pragmas(connection, None)

    cursor.close.assert_called_once_with()
