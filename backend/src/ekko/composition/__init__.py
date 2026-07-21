"""Composition root — DI container and application factory."""

from ekko.composition.app_factory import create_app
from ekko.composition.container import Container

__all__ = ["Container", "create_app"]
