"""Deployment-related enums."""

from __future__ import annotations

from enum import auto, unique

from ekko.core.enums.base import ParseableEnum


@unique
class DeploymentTarget(ParseableEnum):
    """Supported deployment targets."""

    LOCAL = auto()
    DOCKER = auto()
    KUBERNETES = auto()
    AZURE_CONTAINER_APPS = auto()
    AZURE_FUNCTIONS = auto()


@unique
class FeatureFlag(ParseableEnum):
    """Runtime feature toggles."""

    RAG_ENABLED = auto()
    STRUCTURED_LOGGING = auto()


__all__ = ["DeploymentTarget", "FeatureFlag"]
