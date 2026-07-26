"""Tests for config/runtime.py — environment resolution."""

import os
from unittest.mock import patch

from ekko.config.enums import Environment
from ekko.config.runtime import _resolve_runtime_environment


class TestResolveRuntimeEnvironment:
    def test_default_is_local(self):
        with patch.dict(os.environ, {}, clear=True):
            # Remove EKKO_ENVIRONMENT if present
            os.environ.pop("EKKO_ENVIRONMENT", None)
            result = _resolve_runtime_environment()
            assert result == Environment.LOCAL

    def test_resolves_test(self):
        with patch.dict(os.environ, {"EKKO_ENVIRONMENT": "test"}):
            result = _resolve_runtime_environment()
            assert result == Environment.TEST

    def test_resolves_prod(self):
        with patch.dict(os.environ, {"EKKO_ENVIRONMENT": "prod"}):
            result = _resolve_runtime_environment()
            assert result == Environment.PROD

    def test_resolves_dev(self):
        with patch.dict(os.environ, {"EKKO_ENVIRONMENT": "dev"}):
            result = _resolve_runtime_environment()
            assert result == Environment.DEV

    def test_case_insensitive(self):
        with patch.dict(os.environ, {"EKKO_ENVIRONMENT": "LOCAL"}):
            result = _resolve_runtime_environment()
            assert result == Environment.LOCAL

    def test_invalid_falls_back_to_local(self):
        with patch.dict(os.environ, {"EKKO_ENVIRONMENT": "invalid_env_name"}):
            result = _resolve_runtime_environment()
            assert result == Environment.LOCAL
