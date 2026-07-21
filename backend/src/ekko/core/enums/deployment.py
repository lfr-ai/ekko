"""Deployment-related enums."""

from __future__ import annotations

from enum import auto, unique

from ekko.core.enums.base import ParseableEnum


@unique
class DeploymentTarget(ParseableEnum):
    LOCAL = auto()
    DOCKER = auto()
    KUBERNETES = auto()
    AZURE_CONTAINER_APPS = auto()
    AZURE_FUNCTIONS = auto()


@unique
class FeatureFlag(ParseableEnum):
    RAG_ENABLED = auto()
    ENABLE_TELEMETRY = auto()


__all__ = ["DeploymentTarget", "FeatureFlag"]
