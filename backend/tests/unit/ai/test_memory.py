"""Tests for CrewAI memory management."""

import dataclasses

import pytest

from ekko.ai.crewai.memory import (
    ANALYSIS_MEMORY,
    CONVERSATIONAL_MEMORY,
    LIGHTWEIGHT_MEMORY,
    MemoryConfig,
    MemoryManager,
)


class TestMemoryConfig:
    def test_defaults(self):
        cfg = MemoryConfig()
        assert cfg.enabled is True
        assert cfg.short_term is True
        assert cfg.long_term is False
        assert cfg.entity is True
        assert cfg.scoring == "default"
        assert cfg.max_short_term_items == 100
        assert cfg.max_entity_items == 50

    def test_frozen(self):
        cfg = MemoryConfig()
        with pytest.raises(dataclasses.FrozenInstanceError):
            cfg.enabled = False  # type: ignore[misc]


class TestPresetConfigs:
    def test_conversational_memory(self):
        assert CONVERSATIONAL_MEMORY.long_term is True
        assert CONVERSATIONAL_MEMORY.entity is True
        assert CONVERSATIONAL_MEMORY.scoring == "conversational"

    def test_analysis_memory(self):
        assert ANALYSIS_MEMORY.long_term is False
        assert ANALYSIS_MEMORY.entity is True
        assert ANALYSIS_MEMORY.scoring == "analytical"

    def test_lightweight_memory(self):
        assert LIGHTWEIGHT_MEMORY.long_term is False
        assert LIGHTWEIGHT_MEMORY.entity is False
        assert LIGHTWEIGHT_MEMORY.scoring == "default"


class TestMemoryManager:
    def test_default_config(self):
        manager = MemoryManager()
        assert manager.config is LIGHTWEIGHT_MEMORY

    def test_custom_config(self):
        cfg = MemoryConfig(enabled=False)
        manager = MemoryManager(config=cfg)
        assert manager.config is cfg
        assert manager.config.enabled is False

    def test_get_crew_kwargs(self):
        manager = MemoryManager(config=MemoryConfig(enabled=True))
        kwargs = manager.get_crew_kwargs()
        assert kwargs == {"memory": True}

    def test_get_crew_kwargs_disabled(self):
        manager = MemoryManager(config=MemoryConfig(enabled=False))
        kwargs = manager.get_crew_kwargs()
        assert kwargs == {"memory": False}

    def test_apply_to_crew(self):
        """Memory manager applies memory flag to a mock crew."""

        class FakeCrew:
            memory = False

        crew = FakeCrew()
        manager = MemoryManager(config=CONVERSATIONAL_MEMORY)
        result = manager.apply_to_crew(crew)
        assert result.memory is True
